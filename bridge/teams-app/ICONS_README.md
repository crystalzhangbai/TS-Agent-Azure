# Teams App 图标说明

打包 zip 前，这个目录需要两个图标文件（和 manifest.json 平级）：

- `color.png`  — 192 x 192 像素，彩色应用图标
- `outline.png` — 32 x 32 像素，透明背景的白色轮廓图标

可以先用任意占位图。打包命令（在 teams-app 目录内执行）：

```pwsh
Compress-Archive -Path manifest.json,color.png,outline.png -DestinationPath ..\sre-bridge.zip -Force
```

注意：zip 里必须是这三个文件**平铺**，不能带外层文件夹。
