import datetime

class GameTime:
    def __init__(self, start_year=2026, start_month=1, start_day=1):
        self.current_date = datetime.date(start_year, start_month, start_day)
        self.paused = True
        self.speeds = [1, 3, 5, 10]
        self.current_speed_index = 0
        
        # Internal timer to track when a day passes
        self.timer = 0.0
        # Base duration of a day in seconds at 1x speed
        # Adjust this value to change "base" game speed. 
        # e.g. 1.0 means 1 day passes every 1 real second at 1x speed.
        self.seconds_per_day = 1.0 

    def toggle_pause(self):
        self.paused = not self.paused

    def set_speed(self, speed_index):
        if 0 <= speed_index < len(self.speeds):
            self.current_speed_index = speed_index

    def get_speed_multiplier(self):
        return self.speeds[self.current_speed_index]

    def update(self, dt):
        """
        Updates the timer and returns True if a new day has passed.
        dt: delta time in seconds (from pygame.clock.tick / 1000)
        """
        if self.paused:
            return False

        # Accumulate time scaled by speed
        # speed 1x = add dt * 1
        # speed 10x = add dt * 10
        self.timer += dt * self.get_speed_multiplier()

        if self.timer >= self.seconds_per_day:
            # A day (or more) has passed
            days_passed = int(self.timer // self.seconds_per_day)
            self.timer -= days_passed * self.seconds_per_day
            
            # Advance date
            self.current_date += datetime.timedelta(days=days_passed)
            return True # Return True to signal that game logic should update (tick)
        
        return False

    def get_date_string(self):
        return self.current_date.strftime("%d/%m/%Y")
