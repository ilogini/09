# 파일 저장소 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)

---

## 1. Supabase Storage 구성

### 1.1 버킷 구조

| 버킷명 | 용도 | 접근 권한 | 파일 크기 제한 |
|--------|------|----------|-------------|
| `pet-profiles` | 반려동물 프로필 사진 | Public (읽기), Auth (쓰기) | 5MB |
| `walk-photos` | 산책 중 촬영 사진 | Public (읽기), Auth (쓰기) | 10MB |
| `share-cards` | 공유 카드 이미지 | Public (읽기), Auth (쓰기) | 5MB |

### 1.2 디렉토리 구조

```
pet-profiles/
  └── {user_id}/
      └── {pet_id}/
          ├── profile.jpg         ← 대표 프로필 사진
          └── profile_thumb.jpg   ← 썸네일 (200x200)

walk-photos/
  └── {user_id}/
      └── {walk_id}/
          ├── photo_001.jpg       ← 원본
          ├── photo_001_thumb.jpg ← 썸네일 (400x400)
          └── photo_002.jpg

share-cards/
  └── {user_id}/
      └── {walk_id}/
          └── share_card.png      ← 공유용 카드 이미지
```

---

## 2. 업로드 플로우

### 2.1 반려동물 프로필 사진

```typescript
async function uploadPetProfile(petId: string, imageUri: string) {
  // 1. 이미지 리사이즈 (클라이언트)
  const resized = await ImageManipulator.manipulateAsync(
    imageUri,
    [{ resize: { width: 800 } }],
    { compress: 0.8, format: SaveFormat.JPEG }
  );

  // 2. 업로드
  const filePath = `${userId}/${petId}/profile.jpg`;
  const { data, error } = await supabase.storage
    .from('pet-profiles')
    .upload(filePath, resized.blob, {
      contentType: 'image/jpeg',
      upsert: true,
    });

  // 3. Public URL 반환
  const { data: { publicUrl } } = supabase.storage
    .from('pet-profiles')
    .getPublicUrl(filePath);

  // 4. pets 테이블 업데이트
  await supabase.from('pets')
    .update({ photo_url: publicUrl })
    .eq('id', petId);
}
```

### 2.2 산책 사진

```typescript
async function uploadWalkPhoto(walkId: string, imageUri: string, location: LatLng) {
  const fileName = `photo_${Date.now()}.jpg`;
  const filePath = `${userId}/${walkId}/${fileName}`;

  // 1. 리사이즈 + 압축
  const resized = await ImageManipulator.manipulateAsync(
    imageUri,
    [{ resize: { width: 1200 } }],
    { compress: 0.7, format: SaveFormat.JPEG }
  );

  // 2. 업로드
  await supabase.storage
    .from('walk-photos')
    .upload(filePath, resized.blob, {
      contentType: 'image/jpeg',
    });

  const { data: { publicUrl } } = supabase.storage
    .from('walk-photos')
    .getPublicUrl(filePath);

  // 3. walk_photos 테이블에 기록
  await supabase.from('walk_photos').insert({
    walk_id: walkId,
    photo_url: publicUrl,
    location: `POINT(${location.lng} ${location.lat})`,
    taken_at: new Date().toISOString(),
  });
}
```

---

## 3. 이미지 처리

### 3.1 리사이즈 전략

| 용도 | 원본 | 표시용 | 썸네일 |
|------|------|--------|--------|
| 프로필 사진 | 최대 800px | 200x200 (원형 크롭) | 100x100 |
| 산책 사진 | 최대 1200px | 피드: 600px 폭 | 400x400 |
| 공유 카드 | 1080x1920 (Instagram Story) | - | - |

### 3.2 이미지 변환 (Supabase Image Transformation)

```typescript
// Supabase Storage의 이미지 변환 기능 활용
const thumbnailUrl = supabase.storage
  .from('pet-profiles')
  .getPublicUrl(filePath, {
    transform: {
      width: 200,
      height: 200,
      resize: 'cover',
    },
  }).data.publicUrl;
```

---

## 4. 공유 카드 생성

### 4.1 서버 사이드 이미지 생성

산책 완료 시 공유 카드 이미지를 서버에서 생성:

```typescript
// Edge Function에서 Sharp 또는 Canvas 사용
async function generateShareCard(walk: Walk, pet: Pet) {
  // 카드 구성:
  // - 앱 브랜딩 (멍이랑 로고)
  // - 경로 맵 이미지 (Static Map API 캡처)
  // - 반려동물 이름 + 산책 통계
  // - 날짜
  // - 획득 뱃지 (있을 경우)
  // - 앱 다운로드 유도 텍스트

  // 생성된 이미지를 share-cards 버킷에 업로드
  const cardUrl = await uploadShareCard(userId, walk.id, cardBuffer);
  return cardUrl;
}
```

---

## 5. 스토리지 정책 (RLS)

```sql
-- pet-profiles: 본인만 업로드, 모두 읽기
CREATE POLICY "pet_profiles_read" ON storage.objects
  FOR SELECT USING (bucket_id = 'pet-profiles');

CREATE POLICY "pet_profiles_write" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'pet-profiles'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- walk-photos: 본인만 업로드, 피드 공개 사진은 모두 읽기
CREATE POLICY "walk_photos_read" ON storage.objects
  FOR SELECT USING (bucket_id = 'walk-photos');

CREATE POLICY "walk_photos_write" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'walk-photos'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
```

---

## 6. 용량 관리

| 항목 | Free tier | Pro tier |
|------|-----------|---------|
| 총 Storage | 1GB | 100GB |
| 월간 대역폭 | 2GB | 250GB |
| 파일 크기 제한 | 50MB | 5GB |

### 6.1 예상 용량 (MAU 10,000 기준)

| 항목 | 평균 | 월간 예상 |
|------|------|----------|
| 프로필 사진 | 200KB x 1.5 펫/유저 | 3GB |
| 산책 사진 | 300KB x 2장/산책 x 3회/주 | 72GB |
| 공유 카드 | 150KB x 1장/산책 | 18GB |

→ MAU 10,000 시점에서 Pro tier (100GB) 필요

### 6.2 정리 정책

- 30일 이상 접근하지 않은 공유 카드: 삭제
- 계정 삭제 시: 관련 파일 전체 삭제 (30일 유예 후)
- 원본 사진은 영구 보존, 썸네일은 재생성 가능

---

*작성일: 2026-02-12*
*버전: 1.0*
