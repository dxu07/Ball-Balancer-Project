'''!
    @file       taskUser.py
    
    @brief      The task that will run the user interface.
    
    @details    This task takes in keyboard commands from the user to perform 
                certain tasks. This allows for the user to interact with the 
                Encoder and motor tasks to determine instanenous data or to 
                collect data for a period of time. This is done by defining 
                various states that perform different tasks.

                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/16/2022
'''

from time import ticks_us, ticks_diff, ticks_add, ticks_ms
from pyb import USB_VCP
import micropython, shares, array, gc

# Defining the different states of taskUser.py
# Initialization State 
S0_INIT = micropython.const(0)
# Command Center State
S1_CMD = micropython.const(1)
# Zero the encoder State
S2_ZERO = micropython.const(2)
# Output Position State
S3_POSITION = micropython.const(3)
# Output Delta State
S4_DELTA = micropython.const(4)
# Collect Data State
S5_GET = micropython.const(5)
# Stop Data Collection State
S6_STOP = micropython.const(6)
# Output Data State
S7_DATA = micropython.const(7)
# Output Velocity
S8_VEL = micropython.const(8)
# Set Duty for Motor 1 
S9_DUTY1 = micropython.const(9)
# Set Duty for Motor 2
S10_DUTY2 = micropython.const(10)
# Clear Fault
S11_CLRF = micropython.const(11)
# Display Testing UI
S12_THELP = micropython.const(12)
# Motor Testing
S13_TEST = micropython.const(13)
# Set CL Omega
S14_SETOMEGA = micropython.const(14)
# Set CL Gain
S15_SETGAIN = micropython.const(15)
# Toggle CL Control
S16_TOGGLELOOP = micropython.const(16)
# Perform Step Response
S17_STEP = micropython.const(17)
# Output Step Response Data
S18_DATA = micropython.const(18)

S19_Inner_Outer_Gains = micropython.const(19)


def printHelp():
    '''!@brief      This function outputs the GUI of encoder
        @details    The different commands of the user interface is outputted 
                    here.
            
    '''
    print("---------------------------------------------")
    print("Welcome to the platform wizard!")
    print("---------------------------------------------")
    print("Press P to print current position of the ball.")
    print("Press V to print angular velocities of platform.")
    print("Press m to enter duty cycle for motor 1.")
    print("Press M to enter duty cycle for motor 2.")
    print("Press G to collect data for 10s.")
    print("Press S to stop data collection.")
    print("Press K to set closed-loop gain(s).")
    print("Press W to toggle closed-loop control.")
    print("---------------------------------------------")

def InputDutyFCN(char_In, DUTY_str, dFlag):
    '''!@brief      This function reads numeric data
        @details    Based off of the inputs of the user, this function 
                    determines if the input is valid. It ignores all 
                    non-numerical inputs, except for the negative sign (-),
                    the enter key (\r, \n), the period key (.), and the 
                    backspace key (\b, '\x08', \x7F). It also limits the duty 
                    cycle to be between -100% and 100%.
        @param      char_In is the user input from the user
        @param      Duty_str is the existing duty string that is constantly 
                    changing
        @param      dFlag is boolean to signal if enter has been pressed
            
    '''
    if char_In.isdigit() == True:
        DUTY_str += char_In
    elif char_In in {'-'} and len(DUTY_str) == 0:
        DUTY_str += char_In
    elif char_In in {'\b','\x08','\x7F'} and len(DUTY_str)>0:
        DUTY_str = DUTY_str[0:len(DUTY_str)-1]
    elif char_In in {'.'} and DUTY_str.rfind('.') == -1:
        DUTY_str += char_In
    elif char_In in {'\r','\n'}:
        dFlag = True
        if float(DUTY_str) > 100 :
            DUTY_str = "100"
        elif float(DUTY_str) < -100:
            DUTY_str = "-100"
    return DUTY_str, dFlag
        
def InputNumberFCN(char_In, Num_str, eFlag):
    '''!@brief      This function reads numeric data
        @details    Based off of the inputs of the user, this function 
                    determines if the input is valid. It ignores all 
                    non-numerical inputs, except for the negative sign (-),
                    the enter key (\r, \n), the period key (.), and the 
                    backspace key (\b, '\x08', \x7F). It also limits the duty 
                    cycle to be between -100% and 100%.
        @param      char_In is the user input from the user
        @param      Duty_str is the existing duty string that is constantly 
                    changing
        @param      dFlag is boolean to signal if enter has been pressed
            
    '''
    if char_In.isdigit() == True:
        Num_str += char_In
    elif char_In in {'-'} and len(Num_str) == 0:
        Num_str += char_In
    elif char_In in {'\b','\x08','\x7F'} and len(Num_str)>0:
        Num_str = Num_str[0:len(Num_str)-1]
    elif char_In in {'.'} and Num_str.rfind('.') == -1:
        Num_str += char_In
    elif char_In in {'\r','\n'}:
        eFlag = True
    return Num_str, eFlag

def taskUserFcn (taskName, period, Data, Velocity, Duty1, Duty2, clFlag, Kp, Ki, Kd, Position, Contact):
    '''!@brief      This function serves as the main user interface.
        @details    This functions allows for the user to communicate with the 
                    backend using shared data and queues. It allows for the 
                    user to input different commands to perform different 
                    actions like zeroing the position of the encoder, determing 
                    the instantaneous position of the encoder, the change of 
                    position from the most immediate last position to the 
                    current position, and collect data.
        @param      taskName is the name associated the with the taskUser in 
                    main. 
        @param      period is the frequency of which the taskUser is to be run.
        @param      zFlag is the shared variable that communicates the 
                    taskEncoder to determine whether the encoder should be 
                    zeroed or not.
        @param      Data is the share of positional data with 
                    taskEncoder.py.
        @param      Delta is the share of the delta value with 
                    taskEncoder.py.
        @param      Velocity is the share of the velocity value with 
                    taskEncoder.py
        @param      Duty1 is the shared queue containing the requested duty
                    cycle percentage for motor 1.
        @param      Duty2 is the shared queue containing the requested duty
                    cycle percentage for motor 2.
        @param      cFlag is a boolean to signal the clearing of fault 
                    conditions
        
                    
    '''
    # Pre-initialization State
    state = S0_INIT
    start_time = ticks_us()
    next_time = ticks_add(start_time, period)
    
    
    while True:
        
        current_time = ticks_us()
        # position_data = Data.read()
        # delta_data = Delta.read()
        # velocity_data = Velocity.read()
        
        if ticks_diff(current_time, next_time) >= 0:
            
            # Resetting the next_time so that it can apply to the next 
            # iteration of the while loop.
            next_time = ticks_add(next_time, period)
            
            # State 0  (Initialization) 
            if state == S0_INIT :
                ser = USB_VCP()    
                DUTY1 = ""
                DUTY2 = ""
                #omega = ""
                Ki_str = ""
                Kp_str = ""
                Kd_str = ""
                
                ##  @brief      This list is the collection of velocity data
                #   @details    The velocity list is initialized as an empty list. This 
                #               list will be constantly updated in the motor testing state. 
                #
                #velocity_list = []
                
                ##  @brief      Internal boolean to determine if data collection should 
                #               start.
                #   @details    In state 5, data collection for time and position starts. 
                #               This boolean lets the taskUser know that it is time to 
                #               start collecting data.      
                #
                collect_data = False
                
                ##  @brief      Internal boolean to determine if the 'enter' key had been 
                #               pressed in InputDutyFCN().
                #   @details    In order to submit the duty cycle to the duty shares, the 
                #               program must know if the enter key has been pressed. dFlag 
                #               is the signal that it has been pressed. 
                #
                dFlag = False 
                
                ##  @brief      Internal boolean to determine if the 'enter' key had been 
                #               pressed in InputNumberFCN().
                #   @details    In order to submit the omega to the Vref share, the 
                #               program must know if the enter key has been pressed. eFlag 
                #               is the signal that it has been pressed. 
                #
                eFlag = False 
                
                # srFlag = False
                # gain_step = False
                # omega_step = False
                
                enterKp = True
                enterKi = False
                enterKd = False
                outer = False
                
                gc.collect() # Garbage Collection
                
                ##  @brief      The array, timeArray, is the collection of time where
                #               data is being collected.
                #   @details    The timeArray is predefined to collected 3001 data points,
                #               associated with 0-10s. This array is filled in updated time
                #               values when the data collection state is called.
                #  
                timeArray = array.array('h',1001*[0])
                
                ##  @brief      The array, xpositionArray, is the collection of 
                #               x-positions when data is being collected.
                #   @details    The xpositionArray is predefined to collected 1001 data 
                #               points, associated with 0-10s. This array is filled in 
                #               updated position values when the data collection state is 
                #               called.
                #  
                xpositionArray = array.array('f', 1001*[0])
                
                ##  @brief      The array, ypositionArray, is the collection of 
                #               y-positions when data is being collected.
                #   @details    The ypositionArray is predefined to collected 1001 data 
                #               points, associated with 0-10s. This array is filled in 
                #               updated position values when the data collection state is 
                #               called.
                #  
                ypositionArray = array.array('f', 1001*[0])
                
                ##  @brief      The array, xangleArray, is the collection of 
                #               x-Euler angles when data is being collected.
                #   @details    The angleArray is predefined to collected 1001 data 
                #               points, associated with 0-10s. This array is filled in 
                #               updated angle values when the data collection state is 
                #               called.
                #  
                xangleArray = array.array('f', 1001*[0])    
                
                ##  @brief      The array, yangleArray, is the collection of 
                #               y-Euler angles when data is being collected.
                #   @details    The yangleArray is predefined to collected 1001 data 
                #               points, associated with 0-10s. This array is filled in 
                #               updated angle values when the data collection state is 
                #               called.
                #  
                yangleArray = array.array('f', 1001*[0])   
                
                ##  @brief      The array, timeArray, is the collection of time where
                #               data is being collected.
                #   @details    The timeArray is predefined to collected 3001 data points,
                #               associated with 0-30s. This array is filled in updated time
                #               values when the data collection state is called.
                #  
                #timeArray_step = array.array('h',301*[0])
                
                
                ##  @brief      The array, velocityArray, is the collection of velocity 
                #               when data is being collected.
                #   @details    The velocityArray is predefined to collected 3001 data 
                #               points, associated with 0-30s. This array is filled in 
                #               updated velocity values when the data collection state is 
                #               called.
                #  
                #velocityArray_step = array.array('f', 301*[0])
                
                ##  @brief      The array, velocityArray, is the collection of velocity 
                #               when data is being collected.
                #   @details    The velocityArray is predefined to collected 3001 data 
                #               points, associated with 0-30s. This array is filled in 
                #               updated velocity values when the data collection state is 
                #               called.
                #  
                #dutyArray_step = array.array('f', 301*[0])
                
                gc.collect() # Garbage Collection
                
                printHelp()
                state = S1_CMD

            # State 1 (Waiting and looking for character input)
            elif state == S1_CMD:
                
                # Check VCP to see if there is a character waiting.
                # This if statement will primarily handle state transitions.
                if ser.any():
                    # Read one character and decode it into a string
                    charIn = ser.read(1).decode()
                    
                    # if charIn in {'z', 'Z'}:
                    #     print("Zeroing encoder at current position.")
                    #     zFlag.write(True)
                    #     state = S2_ZERO # transition to state 2
                        
                    if charIn in {'p', 'P'}:
                        print("State 3: Print Position")
                        state = S3_POSITION # transition to state 3
                        
                    # elif charIn in {'d', 'D'}:
                    #     print("State 4: Print Delta")
                    #     state = S4_DELTA # transition to state 4
                        
                    elif charIn in {'g', 'G'}:   
                        print("State 5: Collecting Data...")
                        state = S5_GET # transition to state 5
                        
                    elif charIn in {'s', 'S'}:
                        print("State 6: Stopping Data Collection")
                        state = S6_STOP # transition to state 6
                    
                    elif charIn in {'v', 'V'}:
                        print("State 8: Outputting Velocity for Encoder 1:")
                        state = S8_VEL # transition to state 8
                        
                    elif charIn in {'m'}:
                        print("State 9: Setting Duty Cycle for Motor 1.")
                        state = S9_DUTY1 # transition to state 9
                        
                    elif charIn in {'M'}:
                        print("State 10: Setting Duty Cycle for Motor 2.")
                        state = S10_DUTY2 # transition to state 10

                    # elif charIn in {'c', 'C'}:
                    #     print("State 11: Clearing Fault Condition")
                    #     state = S11_CLRF # transition to state 11
                    
                    # elif charIn in {'t', 'T'}:
                    #     print("State 12: Testing.")
                    #     state = S12_THELP # transition to state 12
                        
                    # elif charIn in {'y', 'Y'}:
                    #     print("State 14: Setting Euler Angles.")
                    #     set_prompt = True
                    #     state = S14_SETOMEGA
                        
                    elif charIn in {'k', 'K'}:
                        print("State 19: Setting Gain.")
                        Kp_prompt = True
                        Ki_prompt = True
                        Kd_prompt = True
                        inner = True
                        state = S19_Inner_Outer_Gains
                        
                    elif charIn in {'w', 'W'}:
                        print("State 16: Toggle Closed-Loop Control.")
                        state = S16_TOGGLELOOP
                        
                    # elif charIn in {'r', 'R'}:
                    #     print("State 17: Perform Step Response.")
                    #     srFlag = True
                    #     Num_data_collected_step = 0
                    #     state = S17_STEP
                        
                    else:
                        print(f"You typed {charIn} from state 1")
                        print(f"at t={ticks_diff(current_time,start_time)/1e6}[s].")
            
            # elif state == S2_ZERO:
            #     if zFlag.read() == False:
            #         state = S1_CMD

            elif state == S3_POSITION:
                print(f"The current position is {Position.read()} mm.")
                print(f"The current Euler angles are {Data.read()} degrees.")
                state = S1_CMD

            # elif state == S4_DELTA:
            #     print(f"Delta is currently {delta_data} radians.")
            #     state = S1_CMD
                
            elif state == S5_GET:
                Num_data_collected = 0
                data_start_time = ticks_ms()
                collect_data = True
                state = S1_CMD

            elif state == S6_STOP:
                collect_data = False
                if Num_data_collected > 1:
                    state = S7_DATA
                else:
                    state = S1_CMD
                
            elif state == S7_DATA:
                print("State 7: Outputting Data: (time [s], (x-position, y-position) [mm], (x-angle, y-angle) [deg])")
                for numItems in range(0,Num_data_collected):
                    print(f"{(timeArray[numItems]/1000):.2f}, {(xpositionArray[numItems]):.2f}, {(ypositionArray[numItems]):.2f}, {(xangleArray[numItems]):.2f}, {(yangleArray[numItems]):.2f}")
                state = S1_CMD
                
            elif state == S8_VEL:
                print(f"The current angular velocities for the motors are {Velocity.read()} deg/s.")
                state = S1_CMD
                
            elif state == S9_DUTY1:

                dFlag = False
                if ser.any():
                # Read one character and decode it into a string
                    numIn = ser.read(1).decode()
                    DUTY1, dFlag = InputDutyFCN(numIn,DUTY1,dFlag)
                    
                if dFlag == True:        
                    Duty1.write(float(DUTY1))
                    print(f"Motor 1 duty set to {DUTY1}%.")
                    dFlag = False
                    DUTY1 = ""
                    state = S1_CMD
                    
            elif state == S10_DUTY2:
                dFlag = False
                if ser.any():
                # Read one character and decode it into a string
                    numIn = ser.read(1).decode()
                    DUTY2, dFlag = InputDutyFCN(numIn,DUTY2,dFlag)
                    
                if dFlag == True:
                    Duty2.write(float(DUTY2))
                    print(f"Motor 2 duty set to {DUTY2}%.")
                    dFlag = False
                    DUTY2 = ""
                    state = S1_CMD
                            
            # elif state == S11_CLRF:
            #     cFlag.write(True)
            #     DUTY1 = "0"
            #     DUTY2 = "0"
            #     Duty1.write(float(DUTY1))
            #     Duty2.write(float(DUTY2))
            #     DUTY1 = ""
            #     DUTY2 = ""
            #     state = S1_CMD
                                
            # elif state == S12_THELP:
            #     print("Type a duty % for motor 1 and enter. Type S to exit.")
            #     print("Units displayed as (%, rad/s).")
            #     state = S13_TEST
                
            # elif state == S13_TEST:
            #     if ser.any():
            #     # Read one character and decode it into a string
            #         numIn = ser.read(1).decode()
            #         if numIn in {'s', 'S'}:
            #             print("Leaving testing interface...")
            #             state = S1_CMD
            #         else:
            #             DUTY1, dFlag = InputDutyFCN(numIn,DUTY1,dFlag)
                
            #     # When enter is pressed after entering duty:    
            #     if dFlag == True:
            #         Duty1.write(float(DUTY1))
                    
            #         if len(velocity_list) < 100:
            #             velocity_list.append(velocity_data)
                        
            #         if len(velocity_list) == 100:
            #             # Average the list of 100 velocities
            #             print(f"{DUTY1}, {sum(velocity_list)/len(velocity_list)}")
            #             velocity_list = []
            #             DUTY1 = ""
            #             dFlag = False
            #             state = S13_TEST
            
            # elif state == S14_SETOMEGA:
            #     if set_prompt == True:
            #         print("Enter values for the Euler angles.")
            #         set_prompt = False
                    
            #     if ser.any():
            #     # Read one character and decode it into a string
            #         vNumIn = ser.read(1).decode()
            #         omega, eFlag = InputNumberFCN(vNumIn,omega,eFlag)
            #     if eFlag == True:
            #         print(f"Setting V_ref to {omega} [rad/s].")
            #         Vref.write(float(omega))
            #         eFlag = False
            #         if srFlag == True and gain_step == True:
            #             state = S17_STEP
            #             omega_step = True
            #             omega_test = float(omega)
            #             Vref.write(0)
            #         else:
            #             state = S1_CMD
            #         omega = ''
                    
            #     yield None
            
            # elif state == S15_SETGAIN:
            #     if enterKp == True:
            #         if Kp_prompt == True:
            #             print("Enter a value for Kp.")
            #             Kp_prompt = False
                    
            #         if ser.any():
            #         # Read one character and decode it into a string
            #             KpNumIn = ser.read(1).decode()
            #             Kp_str, eFlag = InputNumberFCN(KpNumIn,Kp_str,eFlag)
            #         if eFlag == True:
            #             print(f"Setting Kp to {Kp_str}.")
            #             Kp.write(float(Kp_str))
            #             eFlag = False
            #             enterKp = False
            #             enterKi = True
            #             Kp_str = ""
        
            #     if enterKi == True:
            #         if Ki_prompt == True:
            #             print("Enter a value for Ki.")
            #             Ki_prompt = False
                    
            #         if ser.any():
            #         # Read one character and decode it into a string
            #             KiNumIn = ser.read(1).decode()
            #             Ki_str, eFlag = InputNumberFCN(KiNumIn,Ki_str,eFlag)
            #         if eFlag == True:
            #             Ki.write(float(Ki_str))
            #             print(f"Setting Ki to {Ki_str}.")
            #             eFlag = False
            #             enterKi = False
            #             enterKd = True
            #             Ki_str = ""
                
            #     if enterKd == True:
            #         if Kd_prompt == True:
            #             print("Enter a value for Kd.")
            #             Kd_prompt = False
                    
            #         if ser.any():
            #         # Read one character and decode it into a string
            #             KdNumIn = ser.read(1).decode()
            #             Kd_str, eFlag = InputNumberFCN(KdNumIn,Kd_str,eFlag)
            #         if eFlag == True:
            #             Kd.write(float(Kd_str))
            #             print(f"Setting Kd to {Kd_str}.")
            #             eFlag = False
            #             enterKp = True
            #             enterKd = False
            #             Kd_str = ""
            #             if srFlag == True:
            #                 state = S17_STEP
            #                 gain_step = True
            #             else:
            #                 state = S1_CMD
                    
            #     yield None
                
            elif state == S16_TOGGLELOOP:
                if clFlag.read() == True:
                    print("Closed-loop is now inactive.")
                    clFlag.write(False)
                    state = S1_CMD
                elif clFlag.read() == False:
                    print("Closed-loop is now active.")
                    clFlag.write(True)
                    state = S1_CMD
                yield None
                
            # elif state == S17_STEP:
            #     # Create srFlag, which, when active, will redirect from S1 back here to S17
            #     if ser.any():
            #     # Read one character and decode it into a string
            #         numIn = ser.read(1).decode()
            #         if numIn in {'s', 'S'}:
            #             print("Leaving testing interface...")
            #             state = S18_DATA
            #             gain_step = False
            #             omega_step = False
            #             srFlag = False
            #     else:
            #         if gain_step == True:
            #             if omega_step == True:
            #                 if Num_data_collected_step == 0:
            #                     step_start_time = ticks_ms()
            #                     step_time = ticks_add(step_start_time, 1000)
                                
            #                 data_current_time_step = ticks_ms()
                            
            #                 if ticks_diff(data_current_time_step, step_time) >= 0:
            #                     # Vref.write(omega_test)
            #                     clFlag.write(True)
            #                     step_time = 100000000000000
                                

            #                 # timeArray_step[Num_data_collected_step] = ticks_diff(data_current_time_step, step_start_time)
            #                 # velocityArray_step[Num_data_collected_step] = velocity_data
            #                 # dutyArray_step[Num_data_collected_step] = Duty1.read()
            #                 Num_data_collected_step += 1
            #                 gc.collect()

            #                 if Num_data_collected_step > 300:
            #                     state = S18_DATA
            #                     gain_step = False
            #                     omega_step = False
            #                     srFlag = False
            #             else:
            #                 state = S14_SETOMEGA
            #         else:
            #             state = S15_SETGAIN
                        
            #         yield None
                
            # elif state == S18_DATA:
            #     print("State 18: Outputting Data. (Time [s], Velocity [rad/s], Duty [%])")
            #     # for numItems in range(0,Num_data_collected_step):
            #     #     print(f"{(timeArray_step[numItems]/1000):.2f}, {(velocityArray_step[numItems]):.2f}, {(dutyArray_step[numItems]):.2f}")
            #     state = S1_CMD
            
            elif state == S19_Inner_Outer_Gains:
                if inner == True:
                    if enterKp == True:
                        if Kp_prompt == True:
                            print("Enter a value for Kp outer.")
                            Kp_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KpNumIn = ser.read(1).decode()
                            Kp_str, eFlag = InputNumberFCN(KpNumIn,Kp_str,eFlag)
                        if eFlag == True:
                            print(f"Setting Kp outer to {Kp_str}.")
                            Kp1 = float(Kp_str)
                            eFlag = False
                            enterKp = False
                            enterKi = True
                            Kp_str = ""
            
                    if enterKi == True:
                        if Ki_prompt == True:
                            print("Enter a value for Ki outer.")
                            Ki_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KiNumIn = ser.read(1).decode()
                            Ki_str, eFlag = InputNumberFCN(KiNumIn,Ki_str,eFlag)
                        if eFlag == True:
                            Ki1 = float(Ki_str)
                            print(f"Setting Ki outer to {Ki_str}.")
                            eFlag = False
                            enterKi = False
                            enterKd = True
                            Ki_str = ""
                    
                    if enterKd == True:
                        if Kd_prompt == True:
                            print("Enter a value for Kd outer.")
                            Kd_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KdNumIn = ser.read(1).decode()
                            Kd_str, eFlag = InputNumberFCN(KdNumIn,Kd_str,eFlag)
                        if eFlag == True:
                            Kd1=float(Kd_str)
                            print(f"Setting Kd outer to {Kd_str}.")
                            eFlag = False
                            enterKp = True
                            enterKd = False
                            inner = False
                            outer = True
                            Kd_str = ""
                            Kp_prompt = True
                            Kd_prompt = True
                            Ki_prompt = True
                            # if srFlag == True:
                            #     state = S17_STEP
                            #     gain_step = True

                if outer == True:
                    if enterKp == True:
                        if Kp_prompt == True:
                            print("Enter a value for Kp inner.")
                            Kp_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KpNumIn = ser.read(1).decode()
                            Kp_str, eFlag = InputNumberFCN(KpNumIn,Kp_str,eFlag)
                        if eFlag == True:
                            print(f"Setting Kp inner to {Kp_str}.")
                            Kp2 = float(Kp_str)
                            eFlag = False
                            enterKp = False
                            enterKi = True
                            Kp_str = ""
            
                    if enterKi == True:
                        if Ki_prompt == True:
                            print("Enter a value for Ki inner.")
                            Ki_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KiNumIn = ser.read(1).decode()
                            Ki_str, eFlag = InputNumberFCN(KiNumIn,Ki_str,eFlag)
                        if eFlag == True:
                            Ki2 = float(Ki_str)
                            print(f"Setting Ki inner to {Ki_str}.")
                            eFlag = False
                            enterKi = False
                            enterKd = True
                            Ki_str = ""
                    
                    if enterKd == True:
                        if Kd_prompt == True:
                            print("Enter a value for Kd inner.")
                            Kd_prompt = False
                        
                        if ser.any():
                        # Read one character and decode it into a string
                            KdNumIn = ser.read(1).decode()
                            Kd_str, eFlag = InputNumberFCN(KdNumIn,Kd_str,eFlag)
                        if eFlag == True:
                            Kd2 =float(Kd_str)
                            print(f"Setting Kd inner to {Kd_str}.")
                            eFlag = False
                            enterKp = True
                            enterKd = False
                            outer = False
                            Kd_str = ""
                            
                            Kp.write((Kp1, Kp2))
                            Kd.write((Kd1, Kd2))
                            Ki.write((Ki1, Ki2))
                            state = S1_CMD
                            # if srFlag == True:
                            #     state = S17_STEP
                            #     gain_step = True
                            # else:
                            #     state = S1_CMD
                        
                    yield None
                    
                    
                yield None
                    

                    
                 
            
            ######################
            # END OF STATE SPACE #
            ######################
            
            else:
                 raise ValueError(f"Invalid state value in {taskName}: State {state} does not exist")
                 
            yield state
            

            
            # Data Collection for State 5
            # (Performing this outside of state 5 allows the system to return to 
            # state 1, where it listens for more commands.)
            if collect_data == True:
                data_current_time = ticks_ms()
                timeArray[Num_data_collected] = ticks_diff(data_current_time, data_start_time)
                xpositionArray[Num_data_collected] = float(Position.read()[0])
                ypositionArray[Num_data_collected] = float(Position.read()[1])
                xangleArray[Num_data_collected] = float(Data.read()[0])
                yangleArray[Num_data_collected] = float(Data.read()[1])
                Num_data_collected += 1
                gc.collect()
            
                if Num_data_collected > 1000:
                    state = S7_DATA
                    collect_data = False
                else: 
                    yield None
            
            else:
                yield None


                
             
        else:
            yield None
                 
                 