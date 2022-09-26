'''!
    @file       touchpanel.py
    
    @brief      Driver to be used with the touch panel.
    
    @details    This driver performs an Xscan, Yscan, and a Zscan on the 
                touchpanel. This returns the x position, y position of the ball.
                It also determines whether or not there is any contact with the
                touch panel. To make the data more accurate, alpha beta 
                filtering is utilized to reduce the noise in the data.

                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       3/16/2022
    
'''
from pyb import Pin, ADC
from time import ticks_us, ticks_diff, sleep_ms, ticks_ms
from ulab import numpy as np


class TouchPanel:
    '''!@brief      The class for initializing, reading, filtering, and 
                    calibrating the 3-wire resistive touch panel.
        @details    This class is responsible for alll of the basic fucntionality
                    of the touch panel.
                    
    '''
    def __init__(self):
        '''!@brief      Initializes the touch panel, creating necessary objects
                        and variables.
            @details    This function initialzes the touch panel pins, creates 
                        a few variables for future use, and creates the Y matrix
                        containing the calibration points.
        '''
        self.Pinym = Pin.cpu.A0
        self.Pinxm = Pin.cpu.A1
        self.Pinyp = Pin.cpu.A6
        self.Pinxp = Pin.cpu.A7
        self.contact = False
        self.initial_time = 0
        self.vx_hat = 0
        self.vy_hat = 0
        self.Cal_step = 0
        self.Calibrated = False
        self.y1_print = True
        self.y2_print = False
        self.y3_print = False
        self.y4_print = False
        self.y5_print = False
        self.Y6_print = False
        self.Y = np.array([[-80, -40], [-80, 40], [80, 40], [80, -40], [0,0]])

    
    def xScan(self):
        '''!@brief      Scans the touch panel for the x-position of the ball.
            @details    This function sets up the touch panel pins to be able
                        to read the position of the ball in the x-direction.
            @return     xpos is the x-position of the ball in ADC units.
            
        '''
        Pin.init(self.Pinxm, mode=Pin.OUT_PP)
        self.Pinxm.low()
        Pin.init(self.Pinxp, mode=Pin.OUT_PP)
        self.Pinxp.high()
        Pin.init(self.Pinyp, mode=Pin.IN)
        self.ymADC = ADC(self.Pinym)
        self.xpos = self.ymADC.read()  #/4095*176-88

        return self.xpos
    
    def yScan(self):
        '''!@brief      Scans the touch panel for the y-position of the ball.
            @details    This function sets up the touch panel pins to be able
                        to read the position of the ball in the y-direction.
            @return     ypos is the y-position of the ball in ADC units.
            
        '''
        Pin.init(self.Pinym, mode=Pin.OUT_PP)
        self.Pinym.low()
        Pin.init(self.Pinyp, mode=Pin.OUT_PP)
        self.Pinyp.high()
        Pin.init(self.Pinxp, mode=Pin.IN)
        self.xmADC = ADC(self.Pinxm)
        self.ypos = self.xmADC.read()  #/4095*100-50
        return self.ypos
    
    def zScan(self):
        '''!@brief      Scans the touch panel to see if the ball is making contact.
            @details    This function sets up the touch panel pins to be able
                        to read read if something is contacting the panel.
            @return     contact is a boolean telling if there is something on the panel.
            
        '''
        Pin.init(self.Pinxm, mode=Pin.OUT_PP)
        self.Pinxm.low()
        Pin.init(self.Pinyp, mode=Pin.OUT_PP)
        self.Pinyp.high()
        
        self.xpADC = ADC(self.Pinxp)
        self.ymADC = ADC(self.Pinym)
        
        if round(self.ymADC.read(), 1) < 4000:          #/4095*3.3,1) != 3.3:
            self.contact = True
        else: 
            self.contact = False
            

        return self.contact

    def Scan(self):
        '''!@brief      Scans the touch panel for the total position of the ball.
            @details    This function sets up the touch panel pins to be able
                        to read the position of the ball in the x-direction, 
                        y-direction, and z-direction (contact). 
            @return     This returns a tuple containing xpos, ypos, contact, 
                        and timespan. The positions are in ADC units and the
                        timespan is in microseconds (for testing).
        '''
        # Timestamp
        start_time = ticks_us()
        
        # Scanning X
        Pin(self.Pinxm, mode=Pin.OUT_PP, value=0)
        Pin(self.Pinxp, mode=Pin.OUT_PP, value=1)
        Pin(self.Pinyp, mode=Pin.IN)
        self.ymADC = ADC(self.Pinym)
        self.xpos = self.ymADC.read()
        
        #Scanning Z
        Pin(self.Pinyp, mode=Pin.OUT_PP, value=1)
        self.xpADC = ADC(self.Pinxp)
        if round(self.ymADC.read(), 1) < 4080:
            self.contact = True
        else: 
            self.contact = False
        
        # Scanning Y
        Pin(self.Pinxp, mode=Pin.IN)
        Pin(self.Pinym, mode=Pin.OUT_PP, value=0)
        self.xmADC = ADC(self.Pinxm)
        self.ypos = self.xmADC.read()
        
        # Timespan Calculation
        end_time = ticks_us()
        time_span = ticks_diff(end_time, start_time)
        
        return (self.xpos, self.ypos, self.contact, time_span)

    def Filter(self, ADC_Data):
        '''!@brief      An alpha-beta filter for removing "noise" from the ADC 
                        position measurements.
            @details    This function uses predictions to filter values from the 
                        touchpanel, making the data more cohesive. 
            @param      ADC_Data is an input to this fucntion: a tuple containing
                        xpos, ypos (ADC units), and contact (boolean).
            @return     This function returns a tuple in the same format as the
                        input, only now it contains filtered xpos and ypos values.
            
        '''
        if self.initial_time == 0:
            self.initial_time = ticks_ms()
            self.x_hat = 0.85*ADC_Data[0]
            self.y_hat = 0.85*ADC_Data[1]
            
        else:
            self.current_time = ticks_ms()
            self.ts = ticks_diff(self.current_time, self.initial_time) # In milliseconds
            self.x_hat = self.x_hat+0.85*(ADC_Data[0]-self.x_hat)+self.ts*self.vx_hat
            self.y_hat = self.y_hat+0.85*(ADC_Data[1]-self.y_hat)+self.ts*self.vy_hat
            self.vx_hat = self.vx_hat + 0.005/self.ts*(ADC_Data[0]-self.x_hat)
            self.vy_hat = self.vy_hat + 0.005/self.ts*(ADC_Data[1]-self.y_hat)
            self.initial_time = self.current_time
            
        return (self.x_hat, self.y_hat, ADC_Data[2])
    
    def Calibrate(self):
        '''!@brief      This function walks the user through the steps to calibrate
                        the touchpanel.
            @details    As the user is instructed to tap 5 points on the touchpanel,
                        this fucntion stores the ADC data points associated with
                        points that were touched. These data points will be used 
                        in Beta(), which will calculate the calibration coefficients
                        based on the positions and ADC data.
            
        '''
        # Calibration recording will have 5 steps
        
        if self.Cal_step == 0:
            if self.y1_print == True:
                print("Touch the bottom left corner.")
                self.y1_print = False 
            if self.zScan() == True:
                self.x1 = self.xScan()
                self.y1 = self.yScan()
                sleep_ms(100)
                self.y2_print = True
            if self.y2_print == True and self.zScan() == False:    
                self.Cal_step += 1
                
        if self.Cal_step == 1:
            if self.y2_print == True:
                print("Touch the top left corner.")
                self.y2_print = False 
            if self.zScan() == True:
                self.x2 = self.xScan()
                self.y2 = self.yScan()
                sleep_ms(100)
                self.y3_print = True
            if self.y3_print == True and self.zScan() == False:    
                self.Cal_step += 1
        
        if self.Cal_step == 2:
            if self.y3_print == True:
                print("Touch the top right corner.")
                self.y3_print = False 
            if self.zScan() == True:
                self.x3 = self.xScan()
                self.y3 = self.yScan()
                sleep_ms(100)
                self.y4_print = True
            if self.y4_print == True and self.zScan() == False:    
                self.Cal_step += 1
                
        if self.Cal_step == 3:
            if self.y4_print == True:
                print("Touch the bottom right corner.")
                self.y4_print = False 
            if self.zScan() == True:
                self.x4 = self.xScan()
                self.y4 = self.yScan()
                sleep_ms(100)
                self.y5_print = True
            if self.y5_print == True and self.zScan() == False:    
                self.Cal_step += 1
                
        if self.Cal_step == 4:
            if self.y5_print == True:
                print("Touch the middle.")
                self.y5_print = False 
            if self.zScan() == True:
                self.x5 = self.xScan()
                self.y5 = self.yScan()
                sleep_ms(100)
                self.Y6_print = True
            if self.Y6_print == True and self.zScan() == False:    
                self.Cal_step += 1
        
        if self.Cal_step == 5:
            if self.Y6_print == True:
                print("Calibration complete.")
                self.Y6_print = False
            self.Calibrated = True
            self.Cal_step = 0
            return (self.Calibrated)

    def Beta(self): 
        '''!@brief      This function uses the 5 data points from the calibration
                        procedure to calculate the matrix of calibration coefficients.
            @details    Using the ADC data from the 5 points tapped on the touch
                        panel, this function calculates the matrix Beta, which 
                        contains the calibration coefficients for the panel.
            @return     Beta is the matrix returned. It contains the 6 numbers 
                        used to calibate the touch panel and convert the ADC units 
                        to units of mm.
            
        '''
        # Creating the Y matrix, containing the coordinates of the 5 test points
        # in millimeters.
        self.X = np.array([[self.x1, self.y1, 1], [self.x2, self.y2, 1], [self.x3, self.y3, 1], [self.x4, self.y4, 1], [self.x5, self.y5, 1]])
        self.X_T = self.X.transpose()
        self.Beta = np.dot(np.dot(np.linalg.inv(np.dot(self.X_T, self.X)), self.X_T), self.Y)
        self.Beta = self.Beta[0,0], self.Beta[0,1], self.Beta[1,0], self.Beta[1,1], self.Beta[2,0], self.Beta[2,1]
        return self.Beta
    
    def Read_Panel(self, Beta):
        '''!@brief      This fucntion is a combination of the scan, filter, and
                        calibration fucntions defined earlier.
            @details    This will scan the x, y, and z components of the touch
                        panel, and filter the data. The filtered data will then 
                        be scaled with the calibration coefficients from the Beta 
                        matrix. 
            @param      Beta is the matrix containing the 6 numbers used to 
                        calibrate the touch panel and convert the ADC units 
                        to units of mm.
            @return     The output of this function is a tuple containing the 
                        filtered and calibrated xpos, ypos (ADC units), contact 
                        (boolean), and time_span (microseconds).
            
        '''
        # Timestamp
        start_time = ticks_us()
        
        ADC_Data = self.Filter(self.Scan())
        self.x_cal = round(Beta[0]*ADC_Data[0] + Beta[1]*ADC_Data[1] + Beta[4], 1)
        self.y_cal = round(Beta[3]*ADC_Data[1] + Beta[2]*ADC_Data[0] + Beta[5], 1)
        
        # Timespan Calculation
        end_time = ticks_us()
        time_span = ticks_diff(end_time, start_time)
        return (self.x_cal, self.y_cal, ADC_Data[2], time_span)
         
if __name__ == '__main__':
    # Adjust the following code to write a test program.
    

    touchpanel = TouchPanel()
    Cal_complete = False
    
    while True:
        if Cal_complete == False:
            Cal = touchpanel.Calibrate()
        if Cal == True:
            Cal_complete = True
            print(f'{Cal}')
            Beta = touchpanel.Beta()
            print(Beta)
            Cal = False
            
        if Cal_complete == True:
            sleep_ms(100)
            Data = touchpanel.Read_Panel(Beta)
            print(f'{Data}')

    
