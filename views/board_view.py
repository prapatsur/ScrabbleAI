def drawLetterPrompt(self, DISPLAYSURF, ALPHASURF):
    # Draw prompt shadow
    ALPHASURF.fill((0, 0, 0, 0))
    pygame.draw.rect(
        ALPHASURF,
        MASK_COLOR,
        (
            Board.PROMPT_LEFT,
            Board.PROMPT_TOP,
            Board.PROMPT_WIDTH + 4,
            Board.PROMPT_HEIGHT + 4,
        ),
    )

    # Draw prompt box
    pygame.draw.rect(
        ALPHASURF,
        (0, 0, 0, 200),
        (
            Board.PROMPT_LEFT - 1,
            Board.PROMPT_TOP - 1,
            Board.PROMPT_WIDTH + 2,
            Board.PROMPT_HEIGHT + 2,
        ),
    )
    pygame.draw.rect(
        ALPHASURF,
        (255, 255, 255, 200),
        (
            Board.PROMPT_LEFT,
            Board.PROMPT_TOP,
            Board.PROMPT_WIDTH,
            Board.PROMPT_HEIGHT,
        ),
    )

    DISPLAYSURF.blit(ALPHASURF, (0, 0))

    # Draw text
    promptText = Board.PROMPT_FONT.render(
        "TYPE A LETTER A-Z", True, (0, 0, 0, 200), (255, 255, 255, 200)
    )
    promptRect = promptText.get_rect()
    promptRect.center = (
        Board.PROMPT_LEFT + Board.PROMPT_WIDTH / 2,
        Board.PROMPT_TOP + Board.PROMPT_HEIGHT / 2,
    )
    DISPLAYSURF.blit(promptText, promptRect)
