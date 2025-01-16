from ezgraphics import GraphicsWindow,  GraphicsMenu
from campo_minato import Partita
class Gui:
    def __init__(self, p:'Partita'):
        self.partita = p
        win_width = 600
        win_height = 600
        self.square_size = min(win_width // self.partita.larghezza, (win_height - 60) // self.partita.altezza)
        # Calcola la dimensione della finestra in base alla larghezza e altezza del campo
        self.window_width = self.partita.larghezza * self.square_size
        self.window_height = (self.partita.altezza * self.square_size) + 60  # Spazio extra per il menu Spazio extra per il menu
        self.win = GraphicsWindow(self.window_width, self.window_height)
        self.win.setTitle("Campo Minato")
        self.canvas = self.win.canvas() 

        # Menu e bottoni centrati nella barra
        button_width_large = 70
        button_width_small = 30
        button_height = 40
        space_between = 10
        button_labels = ["New", "Esci", "↩︎", "↪︎"]

        # Calcolo della larghezza totale necessaria per tutti i bottoni
        total_button_area = (button_width_large * 2) + (button_width_small * 2) + (space_between * (len(button_labels) - 1))
        start_x = (self.window_width - total_button_area) // 2

        # Inizializzazione del dizionario dei bottoni con posizionamento centrato
        self.menu_buttons = {}
        x_position = start_x

        for label in button_labels:
            width = button_width_large if label in ["New", "Esci"] else button_width_small
            self.menu_buttons[label] = (x_position, self.window_height - 50, width, button_height)
            x_position += width + space_between
        self.win.enableEvents("MouseDown", "KeyPress")
        self.win.setEventHandler(self._gestisci_eventi)

        self._disegna_tabellone()
        self._disegna_menu()
        self.win.wait()
    
    def _disegna_menu(self):
        """Disegna la barra orizzontale in basso con i pulsanti."""
        self.canvas.setFill("purple")
        self.canvas.drawRect(0, self.window_height - 60, self.window_width, 60)
        
        # Disegna i pulsanti
        self.canvas.setFill("white")
        for text, (x, y, width, height) in self.menu_buttons.items():
            self.canvas.drawRect(x, y, width, height)
            self.canvas.setTextFont("arial", "bold", 18)
            # Centratura del testo nel bottone
            text_x = x + (width // 2)
            text_y = y + (height // 2)
            self.canvas.drawText(text_x, text_y, text)
        self.canvas.setTextAnchor("center")
            
    def reset_partita(self):
        self.partita.reset()  # Chiama il metodo di reset della partita
        self._disegna_tabellone()  # Riutilizza il reset senza ridondanza
        self._disegna_menu()
        
    def _disegna_tabellone(self):
        self.canvas.clear()
        self.canvas.setFontSize(20)
        self.canvas.setColor("black")
        self.canvas.setLineStyle("solid")
        self.canvas.setTextAnchor("center")
        for row in range(self.partita.altezza):
            for col in range(self.partita.larghezza):
                x = col * self.square_size
                y = row * self.square_size
                state = self._get_cell_state(row, col)
                self.canvas.setFill(state)
                self.canvas.drawRect(x, y, self.square_size, self.square_size)
                # Number of adjacents
                if state == "white" and self.partita.get_mine_adiacenti(row, col):
                    text = str(self.partita.get_mine_adiacenti(row, col))
                    text_x = x + (self.square_size // 2)
                    text_y = y + (self.square_size // 2)
                    # Dizionario colori per ogni numero di mine adiacenti
                    colori_mine = {
                    1: "blue",
                    2: "green",
                    3: "red",
                    4: "purple",
                    5: "maroon",
                    6: "turquoise",
                    7: "black",
                    8: "gray"
                    }

                    # Ottieni il colore dal dizionario (default a nero se non trovato)
                    num_mine = self.partita.get_mine_adiacenti(row, col)
                    colore_testo = colori_mine.get(num_mine, "black")

                    # Imposta il colore e disegna il testo
                    self.canvas.setOutline(colore_testo)
                    self.canvas.drawText(text_x, text_y, text)
                    self.canvas.setColor("black")

        self._disegna_menu()
    
    def _visualizza_game_over(self):
        self._disegna_tabellone()
        self.canvas.setColor("red")
        self.canvas.setTextFont("arial", "bold", 40)
        self.canvas.drawText(self.window_width // 2, self.window_height // 2 -30, "GAME OVER")
       
         
    def _visualizza_vittoria(self):
        self._disegna_tabellone()
        self.canvas.setColor("green")
        self.canvas.setTextFont("arial", "bold", 40)
        self.canvas.drawText(self.window_width // 2, self.window_height // 2 -30, "HAI VINTO")
     
        
    def _get_cell_state(self, row, col) -> str:
        if self.partita.is_coperta(row, col):
            return "red" if self.partita.get_casella_segnata(row, col) else "lightgray"
        elif self.partita.contiene_mina(row, col):
            return "black"
        else:
            return "white"
    
    def _gestisci_eventi(self, window, event):
        """Gestisce gli eventi di mouse e tastiera."""
        if event.type == "MouseDown":
            self._gestisci_click(window, event)
        elif event.type == "KeyPress":
            self._gestisci_tasto(event)
 
    def _gestisci_click(self, window, event):
        col = event.x // self.square_size
        row = event.y // self.square_size
        print(f"Cliccato su: riga={row}, colonna={col}") 
        
        # Controlla se il click è nella barra menu
        for text, (x, y, width, height) in self.menu_buttons.items():
            if x <= event.x <= x + width and y <= event.y <= y + height:
                if text == "New":
                    self.reset_partita()
                elif text == "Esci":
                    self.win.close()
                elif text == "↩︎":
                    self.partita.muovi_mossa("indietro")  # Chiamato il metodo per muovere indietro
                    self._disegna_tabellone()  # Rendi il nuovo stato del tabellone visibile
                elif text == "↪︎":
                    self.partita.muovi_mossa("avanti")  # Chiamato il metodo per muovere avanti
                    self._disegna_tabellone()
                return
        
        if not (0 <= row < self.partita.altezza and 0<= col < self.partita.larghezza):
            return

        if event.button == 1:  # Tasto sinistro del mouse
            self._gestisci_click_sinistro(row, col)
        elif event.button == 2:  # Tasto destro del mouse
            self._gestisci_click_destro(row, col)
        
    def _gestisci_click_sinistro(self, row, col):
        if self.partita.is_coperta(row, col):
            if self.partita.get_casella_segnata(row, col):
                print("Non puoi scoprire una casella segnata.")
            else:
                self.partita.scopriCasella(row, col)  
                stato_partita = self.partita.partita_finita()
                
           
                if stato_partita == "persa":
                    print("Hai colpito una mina! Visualizzazione di tutte le mine...")
                    self.partita.visualizza_mine() 
                    self._visualizza_game_over()
                    self.win.wait() 
                elif stato_partita == "vinta":
                    print("Hai vinto!")
                    self._visualizza_vittoria()
                    self.win.wait() 

                self._disegna_tabellone()

    def _gestisci_click_destro(self, row, col):
        if self.partita.is_coperta(row, col):  # Verifica che la casella sia ancora coperta
            if self.partita.get_casella_segnata(row, col):
                self.partita.segna_casella(row, col)  # Usa segna_casella che rimuove la segnatura
            else:
                self.partita.segna_casella(row, col)  # Usa segna_casella per aggiungere la segnatura
            self._disegna_tabellone()  
            
    def _gestisci_tasto(self, event):
        if event.keycode == 889192475:
            self.partita.visualizza_mine()  
            self._disegna_tabellone() 
            
   

partita = Partita(larghezza=15, altezza=15, n_mine= 15)
gui = Gui(partita)
