#!/bin/bash
DIR="$(dirname "$0")"
cd "$DIR"

for f in *.svg; do
  [ "$f" = "replace_colors.sh" ] && continue

  sed -i \
    -e 's/#c3a1f7/#D4E300/g' -e 's/#a36ff3/#C5D900/g' \
    -e 's/#f2eafd/#F7FBDA/g' -e 's/#e2d1fb/#EBF3A6/g' \
    -e 's/#efe5fd/#F7FBDA/g' -e 's/#d8c2fa/#EBF3A6/g' \
    -e 's/#faf7fe/#FEFEF8/g' -e 's/#e7d9fc/#EBF3A6/g' \
    -e 's/#f5effe/#FAFDE6/g' -e 's/#fbf9fe/#FEFEF8/g' \
    -e 's/#e5d6fc/#EBF3A6/g' -e 's/#fdfcff/#FEFEF8/g' \
    -e 's/#e1d1fb/#EBF3A6/g' -e 's/#e9ddfc/#EBF3A6/g' \
    -e 's/#d6bff9/#E0EC8C/g' -e 's/#d8c2f9/#EBF3A6/g' \
    -e 's/#ebe0fc/#F7FBDA/g' \
    -e 's/#93d4ff/#33BBFF/g' -e 's/#61c0ff/#0099FF/g' \
    -e 's/#33a6ff/#0099FF/g' -e 's/#8ea4ff/#33BBFF/g' \
    -e 's/#bbe4ff/#B3E0FF/g' -e 's/#f3faff/#F0F9FF/g' \
    -e 's/#d4eeff/#CCE9FF/g' -e 's/#ebf7ff/#E6F5FF/g' \
    -e 's/#d2edff/#CCE9FF/g' -e 's/#b6e2ff/#B3E0FF/g' \
    -e 's/#def2ff/#E6F5FF/g' -e 's/#b4e1ff/#B3E0FF/g' \
    -e 's/#f2faff/#F0F9FF/g' -e 's/#c2e7ff/#CCE9FF/g' \
    -e 's/#dff1ff/#E6F5FF/g' -e 's/#addcff/#99D4FF/g' \
    -e 's/#dce3ff/#CCE9FF/g' -e 's/#d9e0ff/#CCE9FF/g' \
    -e 's/#f1f9ff/#F0F9FF/g' -e 's/#bcc8ff/#99D4FF/g' \
    -e 's/#cae8ff/#CCE9FF/g' -e 's/#c5e6ff/#CCE9FF/g' \
    -e 's/#b9e1ff/#B3E0FF/g' -e 's/#a5d8ff/#99D4FF/g' \
    -e 's/#90cfff/#66CCFF/g' -e 's/#d6ecff/#CCE9FF/g' \
    -e 's/#b1dbff/#B3E0FF/g' \
    -e 's/#ffeb86/#E8F060/g' -e 's/#ffbf5b/#C5D900/g' \
    -e 's/#fffac3/#FAFDE6/g' -e 's/#ffeab3/#F7FBDA/g' \
    -e 's/#ffeac9/#F7FBDA/g' -e 's/#fffae1/#FAFDE6/g' \
    -e 's/#ffecbb/#F7FBDA/g' -e 's/#ffe6ae/#EBF3A6/g' \
    -e 's/#ffac72/#D4E300/g' -e 's/#ff846e/#C5D900/g' \
    -e 's/#fff4ed/#FAFDE6/g' -e 's/#ffc8be/#F7FBDA/g' \
    -e 's/#ffcdc5/#F7FBDA/g' -e 's/#fff0e6/#FAFDE6/g' \
    -e 's/#ffd7d0/#EBF3A6/g' -e 's/#ffc8bf/#F7FBDA/g' \
    -e 's/#ffb8e4/#33BBFF/g' -e 's/#ff86b1/#0099FF/g' \
    -e 's/#fff7fc/#F0F9FF/g' -e 's/#ffe8ee/#E6F5FF/g' \
    -e 's/#ffb3c6/#99D4FF/g' -e 's/#fff2fa/#F0F9FF/g' \
    -e 's/#ffccda/#CCE9FF/g' -e 's/#ffedf2/#F0F9FF/g' \
    -e 's/#cde377/#D4E300/g' -e 's/#98d66b/#C5D900/g' \
    -e 's/#e0edab/#EBF3A6/g' -e 's/#d2edc5/#EBF3A6/g' \
    -e 's/#f8fbec/#FAFDE6/g' -e 's/#cfedc3/#EBF3A6/g' \
    -e 's/#ffffec/#FAFDE6/g' -e 's/#dff5ce/#EBF3A6/g' \
    -e 's/#cef1b6/#E0EC8C/g' \
    -e 's/#ffd85e/#D4E300/g' -e 's/#ffb365/#C5D900/g' \
    -e 's/#ffca6f/#D4E300/g' -e 's/#ffb25b/#C5D900/g' \
    -e 's/#fff9e7/#FAFDE6/g' -e 's/#fff2c3/#F7FBDA/g' \
    -e 's/#ffd794/#EBF3A6/g' -e 's/#fff4e0/#FAFDE6/g' \
    -e 's/#ffecd7/#F7FBDA/g' -e 's/#ffdfbf/#EBF3A6/g' \
    -e 's/#ffeca8/#EBF3A6/g' -e 's/#fffdf5/#FEFEF8/g' \
    -e 's/#fffefc/#FEFEF8/g' -e 's/#fffdfc/#FEFEF8/g' \
    -e 's/#fffef8/#FEFEF8/g' -e 's/#fffef9/#FEFEF8/g' \
    "$f"

  echo "Updated: $f"
done

echo "Done! All 24 SVG files processed."
