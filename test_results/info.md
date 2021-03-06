#Test Data Info

The Images in this folder were produced by the recording functions utilized in the main GUI.

The set point data is somewhat flawed however. One of the main reasons being the convoluted way surge and sway (x and y) commands are encapsulated in a single function. 

The set point data was artificial edited to be “correct” for proper visualisation.

The runs are commands sent in a loop delayed by 5 seconds between commands.
Given the overshoot, 5 seconds may not have been 100% sufficient to allow for full settling between commands but overall the performance is illustrated to be quite good.

The parameters utilised for these runs are as follows:
    ```
    SERIAL0_PROTOCOL 2
    AHRS_EKF_TYPE 3
    EK2_ENABLE 0
    EK3_ENABLE 
    VISO_TYPE 1
    EK3_GPS_TYPE 3
    PSC_POSXY_P 2.5
    PSC_POSZ_P  1.0
    PSC_VELXY_D 0.8
    PSC_VELXY_I 0.5
    PSC_VELXY_P 5.0
    PSC_VELZ_P  5.0
    ```
 
Tuning efforts were made but under the time constraints no better results were obtained. These tests and files can be obtained upon request. 

A full auto tune mode could potentially be developed in a similar fashion to what is utilised in ArduCopter, but to tune the Guided Controller gains.
