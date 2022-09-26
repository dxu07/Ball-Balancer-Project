'''!
    @file       taskMotor.py
    
    @brief      The task that interfaces with the motors.
    
    @details    This task's main function is to set the duty cycle of either
                motor while handling external interruptions. This task will be 
                the only task communicating with the motor.py and DRV8847.py 
                driver modules.

                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/16/2022
'''

from time import ticks_us, ticks_add, ticks_diff
import pyb  
import micropython, motor, shares 

# Defining states

# Initialization state
S0_INIT = micropython.const(0)
# Set duty cycle state
S1_SET = micropython.const(1)
# Clear the fault condition state
S2_CLEAR = micropython.const(2)


def taskMotorFcn(taskName, period, Duty1, Duty2):
    '''!@brief      This function interacts with the DRV8847 driver and
                    corresponding motors.
        @details    This function calls upon the driver to set the duty cycle
                    percentage for both motors. After initialization this 
                    fucntion will repeat, setting the speed of each motor
                    to Duty1 and Duty2.
        @param      taskName is the name associated the with taskMotor in 
                    main.py. 
        @param      period determines the frequency at which taskUser is to run.
        @param      Duty1 is the shared queue containing the requested duty
                    cycle percentage for motor 1.
        @param      Duty2 is the shared queue containing the requested duty
                    cycle percentage for motor 2.

    '''
    
    # State 0 is used only for initialization, so it will not exist within 
    # the while loop.
    state = S0_INIT

    start_time = ticks_us()
    next_time = ticks_add(start_time, period)
    
    #nFAULT = pyb.Pin(pyb.Pin.cpu.B2)
    #MotorInt = pyb.ExtInt(nFAULT, mode=pyb.ExtInt.IRQ_FALLING, 
    #                       pull=pyb.Pin.PULL_NONE, callback = motor_drv.fault_cb)
    WM_tim = pyb.Timer(3, freq = 20_000)
    IN1_pin = pyb.Pin.cpu.B4
    IN2_pin = pyb.Pin.cpu.B5
    
    motor_1 = motor.Motor(WM_tim,IN1_pin,IN2_pin,1)
    
    IN3_pin = pyb.Pin.cpu.B0
    IN4_pin = pyb.Pin.cpu.B1
    
    motor_2 = motor.Motor(WM_tim,IN3_pin,IN4_pin,2)
    
    
    Duty1.write(float(0))
    Duty2.write(float(0))

    state = S1_SET
 
    while True:
        current_time = ticks_us()
        if ticks_diff(current_time,next_time)>=0:
            
            # Set 
            if state == S1_SET:
                motor_1.set_duty(Duty1.read()*-1)
                motor_2.set_duty(Duty2.read()*-1)
                
            else: 
                state = 1
                yield state
            next_time = ticks_add(next_time,period)
        else:
            yield None
            
                
    