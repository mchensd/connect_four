from tkinter import *
from Stack import Stack
from PIL import ImageTk

class Application(Frame):
    def __init__(self, master,):
        Frame.__init__(self, master)
        self.grid()
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        '''
        (0,0) - the board
        (0,1) - Who's turn it is
        (1,0) - Extra buttons (undo, help, settings...)
        '''
        self.board = Board(self)
        self.board.grid(row=0, column=0,)

        self.p_moves = Move(self)
        self.p_moves.grid(row=1, column=0)

        self.but_frame = UtilButtons(self)
        self.but_frame.grid(row=0, column=1, rowspan=2, sticky=N)

    def change_moves(self):
        self.p_moves.change_moves()

    def get_curr_move(self):
        return self.p_moves.move
    def display_win(self, move):
        messagebox.showinfo(title="Winner!", message="Player {} won!".format(move))
        self.unbind_all()
        self.but_frame.undo.configure(command=self.but_frame.disabled)

    def undo(self):
        if self.board.undo_stack.len > 0:
            self.board.remove_last_placed()
            self.p_moves.change_moves()
            
    def unbind_all(self):
        for i in range(6):
            for j in range(7):
                circ_id = self.board.coord_to_id(i, j)
                self.board.tag_unbind(circ_id, "<Button-1>")
                self.board.tag_unbind(circ_id, "<Enter>")
                self.board.tag_unbind(circ_id, "<Leave>")

        
        
class Board(Canvas):
    def __init__(self, master,):
        Canvas.__init__(self, master, width=910, height=750, bg="#ffee75")
        self.grid()
        self.board_repr = [[0 for i in range(7)] for j in range(6)]

        self.undo_stack = Stack()
        self.piece_ids = []
        self.master = master
        self.create_canvas_objects()
        
    def create_canvas_objects(self):
        for i in range(6):
            for j in range(7):

                circ_id = self.create_oval(10+j*130, 10+i*120, 120+j*130,
                                  120+i*120, fill="#f2f3f9", tags="piece", width=2)#activeoutline="#d6c942", )
                
                self.piece_ids.append(circ_id)
                def click_handler(event, self=self, col=(circ_id-1) % 7):
                    return self.drop_piece(event, col)

                def enter_handler(event, self=self, col=(circ_id-1) % 7):
                    return self.highlight_column(event, col)

                def leave_handler(event, self=self, col=(circ_id-1) % 7):
                    return self.unhighlight_column(event, col)
                
                self.tag_bind(circ_id, "<Button-1>", click_handler)
                self.tag_bind(circ_id, "<Enter>", enter_handler, add="+colhighlight")
                self.tag_bind(circ_id, "<Leave>", leave_handler, add="+col unhighlight")

    def drop_piece(self, event, col):
        '''handler for left click'''
        colors = ['', '#7e92f7', '#f4777a']  # move is either 1 or 2
        row = None
        move = self.master.get_curr_move()
        color = colors[move]
        for i in range(len(self.board_repr)-1, -1, -1):  # check from bottom up
            if self.board_repr[i][col] == 0:
                self.board_repr[i][col] = move
                p_id = self.coord_to_id(i, col)
                self.itemconfig(p_id, outline="black", fill=color)
                row = i  # remember which row the piece was placed to check if won
                self.undo_stack.push([row, col])
                self.master.change_moves()
                break

        if self.check_win(row, col, move):
            self.master.display_win(move)  # whoever made the move won
    
    
    def get_column(self, c):
        ''' given the column of a piece, return a string of all the pieces in that column '''
        column = ""
        for i in range(6):
            column += str(self.board_repr[i][c])
        return column

    def get_diag_repr(self, r, c, m):
        ''' get all the pieces along the diagonal of piece at r, c, in the slope given '''
        diag = ""
        row = r  # want to keep original r and c
        col = c

        # bad code... I know
        if m == 1:
            while 0 <= row < 6 and 0<= col < 7:
                diag += str(self.board_repr[row][col])
                row += m
                col -= m

            #need to reverse the first part to make the rest of the diagonal consecutive
            diag = list(diag)
            diag.reverse()
            diag = ''.join(diag)
            row = r-1
            col = c+1
            while 0 <= row < 6 and 0<= col < 7:
                diag += str(self.board_repr[row][col])
                row -= 1
                col += 1
        else:
            while 0 <= row < 6 and 0<= col < 7:
                diag += str(self.board_repr[row][col])
                row += 1
                col += 1

            diag = list(diag)
            diag.reverse()
            diag = ''.join(diag)
            row = r-1
            col = c-1
            
            while 0 <= row < 6 and 0<= col < 7:
                diag += str(self.board_repr[row][col])
                row -= 1
                col -= 1
        
        return diag

    def highlight_column(self, event, col):
        '''handler for hovering over a circle'''
        for i in range(len(self.board_repr)):
            if self.board_repr[i][col] == 0:
                p_id = self.coord_to_id(i, col)
                self.itemconfigure(p_id, outline="#d6c942")

    def unhighlight_column(self, event, col):
        '''handler for leaving a circle'''
        for i in range(len(self.board_repr)):
            p_id = self.coord_to_id(i, col)
            self.itemconfigure(p_id, outline="black")        

    def check_win(self, r, c, move):
        '''check if the move made at (r,c) wins'''
        ch_rows = [r-1, r, r+1]
        ch_cols = [c-1, c, c+1]
        reps = []
        reps.append(''.join(list(map(str,self.board_repr[r]))))  # get the row it is in
        reps.append(self.get_column(c))  # get the column it is in

        # get the diagonals it is in (slope = -1, 1)
        reps.append(self.get_diag_repr(r, c, 1))
        reps.append(self.get_diag_repr(r, c, -1))
        
        win_repr = "{}{}{}{}".format(move, move, move, move)   # a win is if there are 4 consecutive pieces of the same move, just check if these are in the
        #diagonals, column, or row
        
        for rep in reps:
            if win_repr in rep:
                return True

        return False
        
    def remove_last_placed(self):
        piece = self.undo_stack.pop()
        row = piece[0]
        col = piece[1]
        # first remove the piece from our inner representation
        self.board_repr[row][col] = 0

        # now remove it from what the user sees
        circ_id = self.coord_to_id(row, col)
        self.itemconfig(circ_id, fill="#f2f3f9")
    
    def coord_to_id(self, x, y):
        return 7*x + y + 1
        
class Move(Frame):
    
    def __init__(self, master,):
        self.bg_color = "#ffffff"
        Frame.__init__(self, master, bg=self.bg_color)
        self.grid()
        self.master = master

        self.columnconfigure(0, minsize=910/2)  # allows for text labels to be stickied
        self.columnconfigure(1, minsize=910/2)
        
        self.move = 1  # player 1's move
        self.font = ("verdana", 16, "bold")
        self.create_widgets()

    def create_widgets(self):
        self.p1 = Frame(self, bg=self.bg_color)
        self.p1.grid(row=0,  column=0, sticky=W)
        
        self.p1_text = Label(self.p1, text="Player 1", font=self.font, bg="yellow", highlightthickness=0)
        self.p1_text.grid(row=0, column=1)

        im_blue = PhotoImage(file="blue.png")
        self.blue = Label(self.p1, image=im_blue)
        self.blue.image = im_blue
        self.blue.grid(row=0,column=0)
        
        self.p2 = Frame(self, bg=self.bg_color)
        self.p2.grid(row=0, column=1, sticky=E)
        
        self.p2_text = Label(self.p2, text="Player 2", font=self.font, bg=self.bg_color,)
        self.p2_text.grid(row=0,column=1,sticky=E)

        im_red = PhotoImage(file="red.png")
        self.red = Label(self.p2, image=im_red)
        self.red.image = im_red
        self.red.grid(row=0, column=0)

    def change_moves(self):
        ''' given who just placed a piece, change moves to the other player '''
        self.move = 1 if self.move == 2 else 2  # change move to the other number
        if self.move == 1:  # changing to player 1's move
            self.p2_text['bg'] = 'white'
            self.p1_text['bg'] = 'yellow'
        else:
            self.p1_text['bg'] = 'white'
            self.p2_text['bg'] = 'yellow'
        
        
class UtilButtons(Frame):
    def __init__(self, master):
        Frame.__init__(self, master,)
        self.grid()
        self.master = master
        self.font = ("verdana", 14)   
        self.create_widgets()

    def disabled(self):  # command for deactivated undo button
        pass
    def create_widgets(self):
        
        self.new_game = Button(self, text="New Game", font=self.font, command=self.master.create_widgets)
        self.new_game.grid()
        
        self.undo = Button(self, text="Undo", font=self.font, command=self.master.undo)
        self.undo.grid()

        
        

tk = Tk()
app = Application(tk)
app.mainloop()
