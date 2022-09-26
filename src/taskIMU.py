'''!
    @file       taskIMU.py
    
    @brief      The task that obtains roll, pitch, and heading data from the 
                BNO055 IMU located on the balancing platform.
    
    @details    This task communicates with the BNO055 driver to obtain values
                for the roll, pitch, and heading of the platform after calibration.
                The IMU data is interpreted and sent off as shares to the other 
                tasks.
    
                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/16/2022
'''

from time import ticks_us, ticks_add, ticks_diff
from pyb import I2C
import BNO055, shares, os

def taskIMUFcn(taskName, period, Data, Velocity):
    '''!@brief      This function interacts with the driver to update the 
                    position.
        @details    This function calls upon the driver the update the position 
                    of the encoder frequently so that the position can be 
                    accurately determined. In addition to updating the 
                    position, it also takes the positional and delta data from 
                    the driver. Furthermore, this function also calls upon the 
                    driver to zero the position when needed.
        @param      taskName is the name associated the with the taskEncoder in 
                    main. 
        @param      period is the frequency of which the taskUser is to be run.
        @param      zFlag is the shared variable that communicates the 
                    taskUser to determine whether the encoder should be 
                    zeroed or not.
        @param      Data is the share of positional data in [rad].
        @param      Delta is the share of change in position data in [rad].
        @param      Velocity is the share of velocity data in [rad/s].

    '''
    
    # State 0 is used only for initialization, so it will not exist within 
    # the while loop.
    state = 0
    i2c = I2C(1, I2C.CONTROLLER)
    IMU = BNO055.BNO055(i2c)

    start_time = ticks_us()
    next_time = ticks_add(start_time, period)
    IMU.mode(1)
    
    isready = False
    filename = "IMU_cal_coeffs.txt"
    
    while True:
        current_time = ticks_us()
        if ticks_diff(current_time,next_time)>=0:
            # State 0 will check calibration.
            if state == 0:
                if isready == True:
                    print("IMU is calibrated.")
                    IMU.mode(1)
                    state = 1
                
                else: # When NOT READY
                    if filename in os.listdir():
                        # File exists, read from it
                        with open(filename, 'r') as f:
                            # Read the first line of the file
                            cal_data_string = f.readline()
                            # Split the line into multiple strings
                            # and then convert each one to a float
                        cal_coeffs = cal_data_string.strip().split(',')
                        coef_array = bytearray(22)
                        for i in range(0, len(cal_coeffs)):
                            cal_coeffs[i] = int(cal_coeffs[i], 16)
                            #cal_coeffs[i] = hex(cal_coeffs[i])
                            coef_array[i] = cal_coeffs[i]
                        IMU.write_coef(coef_array)
                        print("Writing IMU calibration coefficients from file to driver.")
                        isready = True
                        
                    else:
                        # File doesnt exist, calibrate manually and 
                        # write the coefficients to the file
                        if IMU.status() == (3,3,3,0):
                            cal_array = IMU.read_coef()
                            str_list = []
                            for cal_coef in cal_array:
                                str_list.append(hex(cal_coef))
                            with open(filename, 'w') as f:
                                # Perform manual calibration
                                # Then, write the calibration coefficients to the file
                                # as a string. The example uses an f-string, but you can
                                # use string.format() if you prefer
                                f.write(','.join(str_list))
                            print("Writing IMU calibration constants to file.")
                            
                        else:
                            print(f'{IMU.status()}')
                            
                            
            # Update 
            if state == 1:
                
                # Finding position and sharing.
                x, y, z = IMU.read_angle()
                x /= -16
                y /= -16
                z /= -16
                Data.write((x, y, z))
                
                # Finding angular velocity and sharing.
                wx, wy, wz = IMU.read_omega()
                wx /= 16
                wy /= 16
                wz /= 16
                Velocity.write((wx, wy, wz))
                    

            next_time = ticks_add(next_time,period)
        else:
            yield None
            
                
    