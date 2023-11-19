# sudoku_solver
This app is 100% build in Python, the framework for GUI is made with Kivy and tested on Android only.

## Build the APK

Buildozer is used to generate the APK, you can run this command to re-build the APK.

```
buildozer -v android debug
```

## Files

* sudoku.py, class used to describe the grid
* solver.py, class used for resolution
* fast_sudoku.py, class rewrote by Willymontaz much faster but doesn't implement all resolution algo.

## Preview

![](/img/welcome.png "Welcome")
![](/img/empty.png "Empty")
![](/img/error.png "Error")
![](/img/solved.png "Solved")
