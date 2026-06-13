import pygame

class UIManager:
        def __init__(self, screen, title_font, ui_font, width, height, credits_font=None):
            self.screen = screen
            self.title_font = title_font
            self.ui_font = ui_font
            self.credits_font = credits_font if credits_font is not None else ui_font
            self.width = width
            self.height = height
            
            self.bg_color = (10, 5, 25)
            self.credit_bg_color = (5, 5, 20)
            self.normal_color = (255, 255, 255)
            self.hover_color = (0, 255, 255)
            self.shadow_color = (0, 0, 0)
            self.sub_text_color = (180, 180, 180)

        def draw_center_text(self, font, text, y, color):
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(self.width // 2, y))
            self.screen.blit(text_surface, text_rect)
            return text_rect
    

        def draw_button(self, font, text, center_x, center_y):
    
            mouse_pos = pygame.mouse.get_pos()

            preview_surface = font.render(text, True, self.normal_color)
            button_rect = preview_surface.get_rect(center=(center_x, center_y))

            # Add invisible padding
            button_rect.inflate_ip(40, 20)

            is_hovered = button_rect.collidepoint(mouse_pos)
            final_color = self.hover_color if is_hovered else self.normal_color
            display_text = f"> {text} <" if is_hovered else text

            # Shadow improves readability
            shadow_surface = font.render(display_text, True, self.shadow_color)
            shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
            self.screen.blit(shadow_surface, shadow_rect)

            text_surface = font.render(display_text, True, final_color)
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            self.screen.blit(text_surface, text_rect)

            return button_rect


        def start_menu(self,current_time):
            self.screen.fill(self.bg_color)

            self.draw_center_text(self.title_font, "MOON RACE", self.height // 4, (0, 255, 255))
            self.draw_center_text(self.ui_font, "OPERATION REMASTER", self.height // 4 + 70, (220, 220, 220))

            start_button = self.draw_button(self.ui_font, "START GAME", self.width // 2, self.height // 2 + 45)
            instructions_button = self.draw_button(self.ui_font, "INSTRUCTIONS", self.width // 2, self.height // 2 + 95)
            settings_button = self.draw_button(self.ui_font, "SETTINGS", self.width // 2, self.height // 2 + 145)

            # Blinking instruction text.
            if (current_time // 500) % 2 == 0:
                self.draw_center_text(self.ui_font, "PRESS ENTER TO START", self.height - 85, self.normal_color)

            self.draw_center_text(
                self.ui_font,
                "I: INSTRUCTIONS   S: SETTINGS",
                self.height - 45,
                self.sub_text_color
            )

            return start_button, instructions_button, settings_button
    
        def instructions_screen(self):

            self.screen.fill(self.bg_color)

            self.draw_center_text(self.title_font, "HOW TO PLAY", 65, (0, 255, 255))

            controls = [
                "W / A / S / D  or  ARROW KEYS  -  Move Ship",
                "MOUSE  -  Aim Ship",
                "LEFT CLICK  -  Shoot Laser",
                "RIGHT CLICK  -  Super Beam in Level 2",
                "ESC  -  Pause Game",
                "Destroy the target enemies to proceed",
                "Avoid meteors and drones. You only have 3 lives.",
            ]

            y = 155
            for line in controls:
                self.draw_center_text(self.ui_font, line, y, (200, 200, 255))
                y += 42

            start_button = self.draw_button(self.ui_font, "START MISSION", self.width // 2, 485)
            back_button = self.draw_button(self.ui_font, "BACK", self.width // 2, 545)

            self.draw_center_text(
                self.ui_font,
                "ENTER: START   ESC/BACKSPACE: BACK",
                self.height - 25,
                self.sub_text_color
        )

            return start_button, back_button



        def settings_screen(self, volume):
            self.screen.fill(self.bg_color)

            self.draw_center_text(self.title_font, "SETTINGS", 90, (0, 255, 255))
            self.draw_center_text(self.ui_font, "SFX VOLUME", 220, (150, 150, 255))

            bar_x = 200
            bar_y = 275
            bar_width = 400
            bar_height = 22

            pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            fill_width = int(bar_width * volume)
            pygame.draw.rect(self.screen, (100, 100, 255), (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(self.screen, self.normal_color, (bar_x, bar_y, bar_width, bar_height), 2)

            self.draw_center_text(self.ui_font, f"{int(volume * 100)}%", 330, self.normal_color)
            self.draw_center_text(self.ui_font, "UP / DOWN arrows to adjust volume", 410, self.sub_text_color)
            self.draw_center_text(self.ui_font, "ENTER or ESC to go back", 450, (255, 255, 100))

            back_button = self.draw_button(self.ui_font, "BACK", self.width // 2, 520)

            return back_button
        
        def pause_menu(self):
        
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            self.draw_center_text(self.title_font, "MISSION PAUSED", 150, self.normal_color)

            continue_button = self.draw_button(self.ui_font, "CONTINUE", self.width // 2, 280)
            restart_button = self.draw_button(self.ui_font, "RESTART", self.width // 2, 350)
            quit_button = self.draw_button(self.ui_font, "QUIT", self.width // 2, 420)

            self.draw_center_text(
                self.ui_font,
                "ESC: CONTINUE   R: RESTART   Q: QUIT",
                500,
                self.sub_text_color
            )

            return continue_button, restart_button, quit_button

        def end_screen(self, result):
            self.screen.fill(self.bg_color)

            if result == "VICTORY":
                title = "MISSION ACCOMPLISHED"
                subtitle = "The Syndicate swarm has been destroyed."
                color = (50, 255, 100)
            else:
                title = "SIGNAL LOST"
                subtitle = "The Lunar Defender was destroyed."
                color = (255, 50, 50)

            self.draw_center_text(self.title_font, title, 150, color)
            self.draw_center_text(self.ui_font, subtitle, 230, (220, 220, 220))

            restart_button = self.draw_button(self.ui_font, "RESTART MISSION", self.width // 2, 320)
            credits_button = self.draw_button(self.ui_font, "VIEW CREDITS", self.width // 2, 395)
            quit_button = self.draw_button(self.ui_font, "QUIT", self.width // 2, 470)

            self.draw_center_text(
                self.ui_font,
                "R: RESTART   C: CREDITS   Q: QUIT",
                535,
                self.sub_text_color
            )

            return restart_button, credits_button, quit_button

        def credits_screen(self):

            self.screen.fill(self.credit_bg_color)

            self.draw_center_text(self.title_font, "CREDITS", 55, (0, 255, 255))
            self.draw_center_text(self.credits_font, "MOON RACE: OPERATION REMASTER", 140, self.normal_color)

            credits = [
                "Developed by:",
                "",
                "Game Mechanics:",
                "FOO SHENG CHAI, YUU LINN THOON",
                "Enemy AI / Boids System:",
                "FOO SHENG CHAI",
                "Player and Weapons:",
                "FOO SHENG CHAI, YUU LINN THOON",
                "UI, Start Menu, Pause Menu, Instructions, Settings, Ending:",
                "FOO SHENG CHAI, LEON LEE, SABRINA CHUO SEE YING",
                "Assets and Audio: FOO SHENG CHAI",
            ]

            y = 165
            line_gap = 28
            for line in credits:
                color = (0, 255, 255) if line == "Developed by:" else (220, 220, 220)
                self.draw_center_text(self.credits_font, line, y, color)
                y += line_gap

            self.draw_center_text(
                self.credits_font,
                "PRESS ENTER TO RETURN TO START MENU",
                self.height - 75,
                self.normal_color
            )

            self.draw_center_text(
                self.credits_font,
                "PRESS Q TO QUIT",
                self.height - 45,
                self.sub_text_color
            )