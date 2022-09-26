'''!
    @file       taskPanel.py
    
    @brief      Task that interacts with the touch panel driver
    
    @details    This task communicates directly with the touch panel driver. 
                It calibrates the touch panel and reads the position of the 
                ball. It also determines if the ball is on the platform or not.
    
                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/16/2022
'''

from time import ticks_us, ticks_add, ticks_diff
import touchpanel, os

def taskPanelFcn(taskName, period, Position, Contact):
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
        @param      Position is the share of position from the touch panel [mm].


    '''
    
    # State 0 is used only for initialization, so it will not exist within 
    # the while loop.
    state = 0
    TP = touchpanel.TouchPanel()
    Calibrated = False

    start_time = ticks_us()
    next_time = ticks_add(start_time, period)
    last_pos = (0,0)
    Position.write((last_pos))

    
    isready = False
    filename = "TP_cal_coeffs.txt"
    
    while True:
        current_time = ticks_us()
        if ticks_diff(current_time,next_time)>=0:
            # State 0 will check calibration.
            if state == 0:
                if isready == True:
                    print("Touchpanel is calibrated.")
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
                        
                        # coef_array = bytearray(22)
                        for i in range(0, len(cal_coeffs)):
                            cal_coeffs[i] = float(cal_coeffs[i])
    
                        #     coef_array[i] = cal_coeffs[i]
                        # IMU.write_coef(coef_array)
                        Beta = cal_coeffs
                        print("Writing touchpanel calibration coefficients from file to driver.")
                        isready = True
                        
                    else:
                        # File doesnt exist, calibrate manually and 
                        # write the coefficients to the file
                        Calibrated = TP.Calibrate()
                        if Calibrated == True:
                            Beta = TP.Beta()
                            str_list = []
                            for cal_coef in Beta:
                                str_list.append(str(cal_coef))
                            with open(filename, 'w') as f:
                                # Perform manual calibration
                                # Then, write the calibration coefficients to the file
                                # as a string. The example uses an f-string, but you can
                                # use string.format() if you prefer
                                f.write(','.join(str_list))
                            print("Writing touchpanel calibration constants to file.")
                            
                            
                            
            # Update 
            if state == 1:
                
                # Finding position and sharing.
                Data = TP.Read_Panel(Beta)
                x_pos = Data[0]
                y_pos = Data[1]
                contact = Data[2]
                time_span = Data[3] # For testing the speed of the touchpanel updates
                Contact.write(contact)
                
                if contact == True:
                    Position.write((x_pos, y_pos))
                    last_pos = (x_pos, y_pos)
                else:
                    Position.write(last_pos)
                


            next_time = ticks_add(next_time,period)
        else:
            yield None
            
if __name__ == '__main__':
    # Adjust the following code to write a test program.
    while True:    
        taskPanelFcn('TouchPanel', 10_000)
    
    