import random, copy, sys, pygame
from pygame.locals import *

num = {'3': 'Three', '4': 'Four', '5': 'Five'}

DIFFICULTY = 2  # how many moves to look ahead. (>2 is usually too much)

SPACESIZE = 80  # size of the tokens and individual board spaces in pixels

FPS = 60  # frames per second to update the screen
WINDOWWIDTH = 960  # width of the program's window, in pixels
WINDOWHEIGHT = 720  # height in pixels

LIGHTGRAY = (211, 211, 211)
WHITE = (255, 255, 255)
black = (0, 0, 0)
GRAY = (100, 100, 100)

BGCOLOR = LIGHTGRAY
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'

def main():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
    global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
    global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG, n, BOARDWIDTH, BOARDHEIGHT
    global XMARGIN, YMARGIN, CLICKSOUND, HITSOUND

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('In a Row')

    REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    REDTOKENIMG = pygame.image.load('4row_yellow.png')
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load('4row_pink.png')
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load('4row_board.png')
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load('4row_humanwinner.png')
    COMPUTERWINNERIMG = pygame.image.load('4row_computerwinner.png')
    TIEWINNERIMG = pygame.image.load('4row_tie.png')
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    ARROWIMG = pygame.image.load('4row_arrow.png')
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery
    CLICKSOUND = pygame.mixer.Sound("click.wav")
    HITSOUND = pygame.mixer.Sound("hit.wav")

    isFirstGame = True

    n = game_intro()
    pygame.display.set_caption('{} in a Row'.format(num[str(n)]))

    BOARDWIDTH = n + 3  # how many spaces wide the board is
    BOARDHEIGHT = n + 2  # how many spaces tall the board is
    assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

    XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
    YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

    while True:
        runGame(isFirstGame)
        isFirstGame = False


def runGame(isFirstGame):
    if isFirstGame:
        # Let the computer go first on the first game, so the player
        # can see how the tokens are dragged from the token piles.
        turn = COMPUTER
        showHelp = True
    else:
        # Randomly choose who goes first.
        if random.randint(0, 1) == 0:
            turn = COMPUTER
        else:
            turn = HUMAN
        showHelp = False

    # Set up a blank board data structure.
    mainBoard = getNewBoard()

    while True:  # main game loop
        if turn == HUMAN:
            # Human player's turn.
            getHumanMove(mainBoard, showHelp)
            if showHelp:
                # turn off help arrow after the first move
                showHelp = False
            if isWinner(mainBoard, RED, n):
                winnerImg = HUMANWINNERIMG
                break
            turn = COMPUTER  # switch to other player's turn
        else:
            # Computer player's turn.
            column = getComputerMove(mainBoard)
            makeMove(mainBoard, BLACK, column)
            pygame.mixer.Sound.play(HITSOUND)
            if isWinner(mainBoard, BLACK, n):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = HUMAN  # switch to other player's turn

        if isBoardFull(mainBoard):
            # A completely filled board means it's a tie.
            winnerImg = TIEWINNERIMG
            break

    while True:
        # Keep looping until player clicks the mouse or quits.
        drawBoard(mainBoard)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return


def makeMove(board, player, column):
    lowest = getLowestEmptySpace(board, column)
    if lowest != -1:
        board[column][lowest] = player


def drawBoard(board, extraToken=None):
    DISPLAYSURF.fill(BGCOLOR)

    # draw tokens
    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    # draw the extra token
    if extraToken != None:
        if extraToken['color'] == RED:
            DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
        elif extraToken['color'] == BLACK:
            DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    # draw board over the tokens
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    # draw the red and black tokens off to the side
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT) # red on the left
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT) # black on the right


def game_intro():
    intro = True
    pygame.mixer.music.load("song2.wav")
    pygame.mixer.music.play(-1)
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        DISPLAYSURF.fill(LIGHTGRAY)
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects("In a row", largeText, black)
        TextRect.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT / 2) - 100)
        DISPLAYSURF.blit(TextSurf, TextRect)

        pygame.draw.rect(DISPLAYSURF, black, (190, 450, 100, 100))
        pygame.draw.rect(DISPLAYSURF, black, (430, 450, 100, 100))
        pygame.draw.rect(DISPLAYSURF, black, (670, 450, 100, 100))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if 190 + 100 > mouse[0] > 190 and 450 + 100 > mouse[1] > 450:
            pygame.draw.rect(DISPLAYSURF, GRAY, (190, 450, 100, 100))
            if click[0] == 1:
                pygame.mixer.Sound.play(CLICKSOUND)
                game = 3
                return game

        elif 430 + 100 > mouse[0] > 430 and 450 + 100 > mouse[1] > 450:
            pygame.draw.rect(DISPLAYSURF, GRAY, (430, 450, 100, 100))
            if click[0] == 1:
                pygame.mixer.Sound.play(CLICKSOUND)
                game = 4
                return game

        elif 670 + 100 > mouse[0] > 670 and 450 + 100 > mouse[1] > 450:
            pygame.draw.rect(DISPLAYSURF, GRAY, (670, 450, 100, 100))
            if click[0] == 1:
                pygame.mixer.Sound.play(CLICKSOUND)
                game = 5
                return game

        smallText = pygame.font.Font("freesansbold.ttf", 40)
        textSurf1, textRect1 = text_objects("3", smallText, WHITE)
        textRect1.center = ((190 + (100 / 2)), (450 + (100 / 2)))
        DISPLAYSURF.blit(textSurf1, textRect1)

        textSurf2, textRect2 = text_objects("4", smallText, WHITE)
        textRect2.center = ((430 + (100 / 2)), (450 + (100 / 2)))
        DISPLAYSURF.blit(textSurf2, textRect2)

        textSurf3, textRect3 = text_objects("5", smallText, WHITE)
        textRect3.center = ((670 + (100 / 2)), (450 + (100 / 2)))
        DISPLAYSURF.blit(textSurf3, textRect3)

        smallText1 = pygame.font.Font("freesansbold.ttf", 40)
        textSurf4, textRect4 = text_objects("¿Quieres jugar 3, 4 o 5 en raya?", smallText1, black)
        textRect4.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT / 2) + 20)
        DISPLAYSURF.blit(textSurf4, textRect4)


        pygame.display.update()
        FPSCLOCK.tick(FPS)


def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def getNewBoard():
    board = []
    for x in range(n + 3):
        board.append([EMPTY] * (n + 2))
    return board


def getHumanMove(board, isFirstMove):
    draggingToken = False
    tokenx, tokeny = None, None
    while True:
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                # start of dragging on red token pile.
                draggingToken = True
                tokenx, tokeny = event.pos
            elif event.type == MOUSEMOTION and draggingToken:
                # update the position of the red token being dragged
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                # let go of the token being dragged
                if tokeny < YMARGIN and XMARGIN < tokenx < WINDOWWIDTH - XMARGIN:
                    # let go at the top of the screen.
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, column):
                        animateDroppingToken(board, column, RED)
                        board[column][getLowestEmptySpace(board, column)] = RED
                        pygame.mixer.Sound.play(HITSOUND)
                        drawBoard(board)
                        pygame.display.update()
                        return
                tokenx, tokeny = None, None
                draggingToken = False
        if tokenx != None and tokeny != None:
            drawBoard(board, {'x': tokenx - int(SPACESIZE / 2), 'y': tokeny - int(SPACESIZE / 2), 'color': RED})
        else:
            drawBoard(board)

        if isFirstMove:
            # Show the help arrow for the player's first move.
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 1.0

    lowestEmptySpace = getLowestEmptySpace(board, column)

    while True:
        y += int(dropSpeed)
        dropSpeed += 0.5
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
            return
        drawBoard(board, {'x': x, 'y': y, 'color': color})
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def animateComputerMoving(board, column):
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    speed = 1.0
    # moving the black tile up
    while y > (YMARGIN - SPACESIZE):
        y -= int(speed)
        speed += 0.5
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    # moving the black tile over
    y = YMARGIN - SPACESIZE
    speed = 1.0
    while x > (XMARGIN + column * SPACESIZE):
        x -= int(speed)
        speed += 0.5
        drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    # dropping the black tile
    animateDroppingToken(board, column, BLACK)


def getComputerMove(board):
    potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)
    # get the best fitness from the potential moves
    bestMoveFitness = -1
    for i in range(BOARDWIDTH):
        if potentialMoves[i] > bestMoveFitness and isValidMove(board, i):
            bestMoveFitness = potentialMoves[i]
    # find all potential moves that have this best fitness
    bestMoves = []
    for i in range(len(potentialMoves)):
        if potentialMoves[i] == bestMoveFitness and isValidMove(board, i):
            bestMoves.append(i)
    return random.choice(bestMoves)


def getPotentialMoves(board, tile, lookAhead):
    if lookAhead == 0 or isBoardFull(board):
        return [0] * BOARDWIDTH

    if tile == RED:
        enemyTile = BLACK
    else:
        enemyTile = RED

    # Figure out the best move to make.
    potentialMoves = [0] * BOARDWIDTH
    for firstMove in range(BOARDWIDTH):
        dupeBoard = copy.deepcopy(board)
        if not isValidMove(dupeBoard, firstMove):
            continue
        makeMove(dupeBoard, tile, firstMove)
        if isWinner(dupeBoard, tile, n):
            # a winning move automatically gets a perfect fitness
            potentialMoves[firstMove] = 1
            break  # don't bother calculating other moves
        else:
            # do other player's counter moves and determine best one
            if isBoardFull(dupeBoard):
                potentialMoves[firstMove] = 0
            else:
                for counterMove in range(BOARDWIDTH):
                    dupeBoard2 = copy.deepcopy(dupeBoard)
                    if not isValidMove(dupeBoard2, counterMove):
                        continue
                    makeMove(dupeBoard2, enemyTile, counterMove)
                    if isWinner(dupeBoard2, enemyTile, n):
                        # a losing move automatically gets the worst fitness
                        potentialMoves[firstMove] = -1
                        break
                    else:
                        # do the recursive call to getPotentialMoves()
                        results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
                        potentialMoves[firstMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
    return potentialMoves


def getLowestEmptySpace(board, column):
    # Return the row number of the lowest empty row in the given column.
    for y in range(BOARDHEIGHT-1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1


def isValidMove(board, column):
    # Returns True if there is an empty space in the given column.
    # Otherwise returns False.
    if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
        return False
    return True


def isBoardFull(board):
    # Returns True if there are no empty spaces anywhere on the board.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == EMPTY:
                return False
    return True


def isWinner(board, tile, game):
    if game == 3:
        # check horizontal spaces
        for x in range(BOARDWIDTH - 2):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x + 1][y] == tile and board[x + 2][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 2):
                if board[x][y] == tile and board[x][y + 1] == tile and board[x][y + 2] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 2):
            for y in range(2, BOARDHEIGHT):
                if board[x][y] == tile and board[x + 1][y - 1] == tile and board[x + 2][y - 2] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 2):
            for y in range(BOARDHEIGHT - 2):
                if board[x][y] == tile and board[x + 1][y + 1] == tile and board[x + 2][y + 2] == tile:
                    return True
    elif game == 4:
        # check horizontal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x + 1][y] == tile and board[x + 2][y] == tile and board[x + 3][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x][y + 1] == tile and board[x][y + 2] == tile and board[x][y + 3] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if board[x][y] == tile and board[x + 1][y - 1] == tile and board[x + 2][y - 2] == tile and board[x + 3][y - 3] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x + 1][y + 1] == tile and board[x + 2][y + 2] == tile and board[x + 3][y + 3] == tile:
                    return True
    else:
        # check horizontal spaces
        for x in range(BOARDWIDTH - 4):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile and board[x+4][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 4):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile and board[x][y+4] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 4):
            for y in range(4, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile and board[x+4][y-4] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 4):
            for y in range(BOARDHEIGHT - 4):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile and board[x+4][y+4] == tile:
                    return True
    return False


if __name__ == '__main__':
    main()
