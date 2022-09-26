'''!@file                       mainpage.py
    @brief                      Creates the main documentation page for the ME 305 final project.
    @details                    This file serves the sole purpose of generating html
                                documentation for the final ball-balancing project.
    @mainpage                   ME 305 Final Project: Ball Balancer

    @section sec_intro          Introduction
                                The ME 305 final project relies on the use of 11 files
                                that work in tandem to balance a ball on a tilting
                                platform. These micropython files are flashed onto a
                                Nucleo STM32 microcontroller, which acts as the controller
                                for this dynamic system. The controller uses information
                                from the BNO055 IMU to keep track of the x and y angles
                                of the platform, while also using a resistive touchpanel
                                to know the x and y position of the ball. With this
                                information, the controller is able to calculate the
                                appropriate duty cycles for each motor at any point in
                                time so that that ball stays as close to the center of
                                the platform as possible.

    @section sec_demo           Demonstration of Ball-Balancing
                                The following video shows a demonstration of our platform
                                in closed-loop control mode as it balances a steel ball.
                                We were able to tune our cascaded controllers through a
                                long process of guessing and checking. After some time, we
                                were able to find gain values that can keep the ball balanced
                                for over a minute.

    @htmlonly           <iframe src="https://player.vimeo.com/video/689423266?h=e72dabe2a9&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" width="720" height="405" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen title="ME 305 Final Project - Ball Balancing"></iframe>
                        <br>
    @endhtmlonly

    @section sec_files          Files in the Final Project
                                Considering a file hierarchy consisting of 3 layers,
                                main.py and shares.py make up the high level layer.
                                This layer instantiates objects and runs tasks.
                                The middle layer is made up our our four tasks:
                                taskUser.py, taskIMU.py, taskPanel.py, taskController.py and
                                taskMotor.py which run sequentially, each with a period
                                of 0.01 [s]. The bottom layer is the driver layer which
                                consists of the drivers: BNO055.py, motor.py,
                                touchpanel.py, and ClosedLoop.py. Each of these drivers
                                is designed to be reusable, controlling only the most
                                basic functionality of each of the physical components
                                they represent.

    @section sec_deliv          Final Lab Deliverables
                                To dive further into the specifics of this final project, some additional details are provided below.

    @subsection sec_deliv1      Task Diagrams
                                The following diagram shows how the 5 middle-tier task
                                files interact with each other using shares. Each of the
                                tasks in our program is run at the same frequency of
                                100 Hz.
                                
                                \n
                                
    @htmlonly           <a href="https://ibb.co/gyrkwW3"><img src="https://i.ibb.co/9npQ24N/Page1.png" alt="Page1" border="0"></a>
    @endhtmlonly

    @subsection sec_deliv2      State Transition Diagrams
                                The following state transition diagrams show how each
                                of our 5 task files operates as a finite state machine.

    @htmlonly           <a href="https://ibb.co/X8YQBnS"><img src="https://i.ibb.co/k1m7nLQ/Page2.png" alt="Page2" border="0"></a>
                        <a href="https://ibb.co/86cgKQ6"><img src="https://i.ibb.co/vZY4wMZ/Page3.png" alt="Page3" border="0"></a>
                        <a href="https://ibb.co/26frW8k"><img src="https://i.ibb.co/8BSwNz7/Page4.png" alt="Page4" border="0"></a>
                        <a href="https://ibb.co/1mV5KdL"><img src="https://i.ibb.co/CHdZvMz/Page5.png" alt="Page5" border="0"></a>
                        <a href="https://ibb.co/bQ3ccqY"><img src="https://i.ibb.co/k5yNNkz/Page6.png" alt="Page6" border="0"></a>
    @endhtmlonly

    @section sec_userint        User Interface
                                The user interface we constructed for this lab is very
                                simple, but it operates smoothly and allows for multiple
                                types of user input. The image below shows the "platform
                                wizard" help menu that pops up when you first start up
                                the microcontroller.

    @htmlonly           <a href="https://ibb.co/XjsdrRz"><img src="https://i.ibb.co/mbqYVWH/Putty-GUI.png" alt="Putty-GUI" border="0"></a>
    @endhtmlonly

    @subsection sec_UIvid       Video of UI
                                The following video shows a quick demonstration of our
                                simple user interface from within PuTTY. This video
                                demonstrates the functionality of each of the menu
                                items in our "platform wizard" help menu.

    @htmlonly           <iframe src="https://player.vimeo.com/video/689477813?h=193cfd8feb&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" width="720" height="388" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen title="ME 305 Final Project - User Interface Tour"></iframe>
    @endhtmlonly

    @subsection sec_datavid     Video of Data Recording
                                The following video shows that the ball's
                                position data and the platform's angular orientation
                                are recorded over a 10 second period after the "G" key
                                is pressed. This data is printed into PuTTY, where we
                                can copy it over to Excel to plot later on.

    @htmlonly           <iframe src="https://player.vimeo.com/video/689423559?h=4541d24ba6&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" width="720" height="405" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen title="ME 305 Final Project - Data Recording and UI"></iframe>
    @endhtmlonly

    @subsection sec_recdata        Recorded Data
                                After taking the data printed to our serial interface
                                (PuTTY), we generated the following plots to show the
                                performance of our balancing platform. The data used in
                                these plots is from the same trial seen in the video
                                shown above. It can be seen that all of the plots
                                oscillate near or around zero. It can also be seen that
                                the ball's x position is trailing the Y-angle while the
                                y position trails the x angle.

    @htmlonly           <a href="https://ibb.co/kSvFDYt"><img src="https://i.ibb.co/87tVxFH/Trial-run-plots.png" alt="Trial-run-plots" border="0"></a>
                        <br>
    @endhtmlonly

    @author             Daniel Xu
    @author             Jake Lesher

    @copyright          License Info
    @date               March 3, 2022
'''
