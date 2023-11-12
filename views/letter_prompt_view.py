class LetterPromptView:
    def __init__(self, display_surf, alpha_surf):
        self.DISPLAYSURF = display_surf
        self.ALPHASURF = alpha_surf

    def draw(self):
        """ Draws a letter prompt to ask for the blank letter """
        # Draw prompt shadow
        self.ALPHASURF.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.ALPHASURF,
            MASK_COLOR,
            (
                PROMPT_LEFT,
                PROMPT_TOP,
                PROMPT_WIDTH + 4,
                PROMPT_HEIGHT + 4,
            ),
        )

        # Draw prompt box
        pygame.draw.rect(
            self.ALPHASURF,
            (0, 0, 0, 200),
            (
                PROMPT_LEFT - 1,
                PROMPT_TOP - 1,
                PROMPT_WIDTH + 2,
                PROMPT_HEIGHT + 2,
            ),
        )
        pygame.draw.rect(
            self.ALPHASURF,
            (255, 255, 255, 200),
            (
                PROMPT_LEFT,
                PROMPT_TOP,
                PROMPT_WIDTH,
                PROMPT_HEIGHT,
            ),
        )

        self.DISPLAYSURF.blit(self.ALPHASURF, (0, 0))

        # Draw text
        PROMPT_FONT = pygame.font.Font("freesansbold.ttf", 20)
        promptText = PROMPT_FONT.render(
            "TYPE A LETTER A-Z", True, (0, 0, 0, 200), (255, 255, 255, 200)
        )
        promptRect = promptText.get_rect()
        promptRect.center = (
            PROMPT_LEFT + PROMPT_WIDTH / 2,
            PROMPT_TOP + PROMPT_HEIGHT / 2,
        )
        self.DISPLAYSURF.blit(promptText, promptRect)