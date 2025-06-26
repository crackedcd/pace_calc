# pace_calc
长跑配速计算器

适配windows 10/11

（依赖MSVC编译器 https://visualstudio.microsoft.com/visual-cpp-build-tools/）

python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=pyside6 --include-qt-plugins=sensible --nofollow-import-to=tests,unittest --remove-output --output-dir=build pace_calc.py


功能参考：https://dingxuan.info/calc/index.php
