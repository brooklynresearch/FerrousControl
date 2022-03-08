# nstokes version 2
### 40 x 46 magnets

#### Launch Command
```
java -jar processing-py.jar nstokes_2_40x46.pyde
```

#### Keyboard Controls
* `s` Toggle SNEK mode
* `m` Toggle MORPH mode
* `t` Toggle test sequence (if snek or morph is active, toggle that off before using this)
* `o` All magnets on
* `r` Reset all to 0
* `f` Activate area around mouse pointer
* `d` Activate single magnet under mouse pointer

#### Notes

To change the parser board USB addresses, edit the [serialAddresses array](https://github.com/brooklynresearch/FerrousControl/blob/772c967f043f15182d9b4fa4592e4093779d1fde/COMMS/PYTHON/nstokes_2_40x46/nstokes_2_40x46.pyde#L53)

To have the program run the test sequence only, set [DEBUG_MODE](https://github.com/brooklynresearch/FerrousControl/blob/772c967f043f15182d9b4fa4592e4093779d1fde/COMMS/PYTHON/nstokes_2_40x46/nstokes_2_40x46.pyde#L25)

**Possible issue**: I've had to restart the parser boards to get the magnet indexing correct. This seems to happen when connecting a magnet controller (or chain of them) to one of the parser's RJ45 ports **after** running the processing sketch.
Sometimes, subsequent runs will have incorrect indexing for the packet that gets sent to the magnet boards. For example, the boards in the lower half will be one row off until a parser restart.
Replugging the USB hub to the computer fixes it. **Needs more testing**
