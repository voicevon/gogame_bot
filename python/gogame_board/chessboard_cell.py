

class ChessboardCell():
    
    def __init__(self):
        self.__col_name_list = 'ABCDEFGHJKLMNOPQRST'
        self.name = 'A1'
        self.row_id = 0
        self.col_letter = 'A'
        self.col_id = 0
        self.id = 0


    def from_id(self, cell_id):
        '''
        cell_id range is (0,360)
        '''
        if cell_id < 0 or cell_id > 361:
            print('[Error]: ChessboardCell::from_id()')
            raise Exception

        row_id = int(cell_id / 19) 
        col_id = cell_id % 19
        self.from_col_row_id(col_id=col_id, row_id=row_id )
        return self

    def from_col_row_id(self, col_id, row_id):
        '''
        From the point of view of camera, The sequence is from top right to bottom left
        Examaple: The name Q4 means Column_name='4', Row_name='Q'.
        col_id = [0..18]    A...T,  from right to left
        row_id = [0..18]    1..19,   from top to bottom   
        '''
        self.row_id = row_id
        self.col_id = col_id
        self.id = row_id * 19 + col_id
        self.col_letter = self.__col_name_list[18-col_id:19-col_id]
        self.name = self.col_letter + str(self.row_id + 1)
        return self
    
    def from_name(self,name):
        # print('For very rare bug..... cell name = %s' %name)
        if name=='resign':
            xx= input ('computer_playing, cell_name="resign", press enter to continue')
            # name = 'T0'
            return None
        col_id = 18 - self.__col_name_list.find(name[:1])
        row_id = int(name[1:]) -1    # exeption here:
        self.from_col_row_id(col_id,row_id)
        return self
    
    def to_diction(self):
        target_diction = {'id':self.id, 'name':self.name, 'row_id':self.row_id, 'col_id':self.col_id,'col_leter':self.col_letter}
        return target_diction

    def to_camera__board_xy(self):
        x = 22 * (18 - self.col_id) + 16
        y = 22 * (18 - self.row_id) + 16
        return (x,y)

if __name__ == "__main__":
    cell = ChessboardCell()
    cell.from_name('T1')
    print(cell.to_diction())