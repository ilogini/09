$dir = 'D:\claude\website_plan\pds\2026\토이 프로젝트\withBowwow\design\연주\소스\글라스모피니즘 아이콘\소스1'
$files = Get-ChildItem -Path $dir -Filter '*.svg'
Write-Host "Found $($files.Count) SVG files"

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $hasOldColor = $content.Contains('#c3a1f7') -or $content.Contains('#93d4ff') -or $content.Contains('#ffeb86') -or $content.Contains('#cde377')
    Write-Host "$($file.Name): length=$($content.Length), hasOldColor=$hasOldColor"
}
