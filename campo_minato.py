import random
from typing import List


class Tabellone:
    def __init__(self, p:'Partita'):
        self.righe = p.altezza
        self.colonne = p.larghezza
        self.tabella = [['C' for _ in range(self.colonne)] for _ in range(self.righe)]
        self.mine = set(random.sample(range(self.righe * self.colonne), p.n_mine))
        self.segnate = set()
        self.scoperte =set()
           
            
    @classmethod
    def copia_tabellone(cls, t:'Tabellone') -> 'Tabellone':
        copia = cls.__new__(cls)
        copia.righe = t.righe
        copia.colonne = t.colonne
        copia.tabellone = [riga[:] for riga in t.tabella]  # Copia profonda
        copia.mine = t.mine.copy()
        copia.segnate = t.segnate.copy()
        copia.scoperte = t.scoperte.copy()
        return copia

    
    def segna_casella(self, riga:int, colonna:int) -> None:
        idx = riga * self.colonne + colonna
        if idx in self.segnate:
            self.segnate.remove(idx)
        else:
            self.segnate.add(idx)
            
         
    def is_segnata(self, riga:int, colonna:int) -> bool:
        return (riga * self.colonne + colonna) in self.segnate
        
    
    def scopri_casella(self, riga:int, colonna:int) -> None:
        idx = riga * self.colonne + colonna
        self.scoperte.add(idx)
        
        
    def is_coperta(self, riga: int, colonna: int) -> bool:
        idx = riga * self.colonne + colonna
        return idx not in self.scoperte

    def mine_adiacenti(self, riga, colonna):
        """
        Calcola il numero di mine adiacenti a una casella specificata.
        """
        mine_adiacenti = [0] * (self.righe * self.colonne)
        for riga in range(self.righe):
            for colonna in range(self.colonne):
                idx = riga * self.colonne + colonna
                if idx in self.mine:
                    continue
                # Calcola il numero di mine adiacenti alla casella
                count = 0
                adjacent = [(riga + dr, colonna + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
                for r, c in adjacent:
                    if 0 <= r < self.righe and 0 <= c < self.colonne:
                        if (r * self.colonne + c) in self.mine:
                            count += 1
                mine_adiacenti[idx] = count
        return mine_adiacenti
    
    def __str__(self) -> str:
        result = []
        for r in range(self.righe):
            row = []
            for c in range(self.colonne):
                idx = r * self.colonne + c
                if idx in self.scoperte:
                    if idx in self.mine:
                        row.append("Z")
                    else:
                        row.append(str(self.mine_adiacenti(r, c)))
                elif idx in self.segnate:
                    row.append("D" if idx not in self.mine else "Y")
                else:
                    row.append("C" if idx not in self.mine else "X")
            result.append("".join(row))
        return "\n".join(result)
    
    
# ——————————————————————————————————————————————————————————————————————————————————————–————   
    
class Partita:
    def __init__(self, larghezza: int, altezza: int, n_mine: int):
        """
        Costruttore che inizializza la partita con un tabellone di dimensioni larghezza x altezza e n_mine mine.
        """
        self._larghezza = larghezza
        self._altezza = altezza
        self._n_mine = n_mine
        self._stato_corrente = 0  # 0 -> in corso, 1 -> successo, 2 -> fallimento
        self._tabellone = Tabellone(self)
        self._evoluzione = [Tabellone.copia_tabellone(self.tabellone)]
        self._mosse = []  # Lista per memorizzare le mosse effettuate

        
    def _aggiorna_evoluzione(self):
        """
        Aggiunge l'attuale stato del tabellone alla lista di evoluzione
        """
        self.evoluzione.append(Tabellone.copia_tabellone(self.tabellone))
            
    @property
    def larghezza(self) -> int:
        return self._larghezza

    @property
    def altezza(self) -> int:
        return self._altezza

    @property
    def n_mine(self) -> int:
        return self._n_mine

    @property
    def stato_corrente(self) -> int:
        return self._stato_corrente
    
    @stato_corrente.setter
    def stato_corrente(self, valore):
        self._stato_corrente = valore
        
    @property
    def tabellone(self) -> int:
        return self._tabellone
    
    @property
    def evoluzione(self) -> list:
        """
        Restituisce la lista dei tabelloni evoluti durante la partita.
        """
        return self._evoluzione

    @evoluzione.setter
    def evoluzione(self, valore: list) -> None:
        self._evoluzione = valore
    
    def segna_casella(self, riga: int, colonna: int) -> None:
        if self.stato_corrente != 0:
            raise RuntimeError("La partita non è in corso.")
        if not self._tabellone.is_coperta(riga, colonna):
            raise ValueError("La casella è già scoperta.")
        
        self._tabellone.segna_casella(riga, colonna)
        self._mosse.append((riga, colonna)) 
        self._aggiorna_evoluzione()
            
    def get_casella_segnata(self, riga: int, colonna: int) -> bool:
        return self.tabellone.is_segnata(riga, colonna)

    def scopriCasella(self, riga: int, colonna: int) -> None:
        
        if self.stato_corrente != 0:
            raise RuntimeError("La partita non è in corso.")
        if self.get_casella_segnata(riga, colonna):
            raise ValueError("La casella è segnata come mina.")
        
        idx = riga * self.larghezza + colonna

        self._aggiorna_evoluzione()
        if idx in self.tabellone.mine:
            self.tabellone.scopri_casella(riga, colonna)
            self.stato_corrente = 2  # Partita terminata senza successo
            return 
        else:
            self._scopri_ricorsivo(riga, colonna)

            if all(
                (r * self.larghezza + c) in self.tabellone.mine or not self._tabellone.is_coperta(r, c)
                for r in range(self.altezza) for c in range(self.larghezza)
            ):
                self.stato_corrente = 1  # Partita terminata con successo
        
        self._aggiorna_evoluzione()
        self._mosse.append((riga, colonna))       

        
    def _scopri_ricorsivo(self, riga: int, colonna: int):
        if not (0 <= riga < self.altezza and 0 <= colonna < self.larghezza):
            return
        if not self._tabellone.is_coperta(riga, colonna):
            return

        self._tabellone.scopri_casella(riga, colonna)

        if self.tabellone.mine_adiacenti(riga, colonna) == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr != 0 or dc != 0:
                        self._scopri_ricorsivo(riga + dr, colonna + dc)

    def get_mine_adiacenti(self, riga: int, colonna: int) -> int:
        return self._tabellone.mine_adiacenti(riga, colonna)

    def contiene_mina(self, riga: int, colonna: int) -> bool:
        idx = riga * self.larghezza + colonna
        return idx in self._tabellone.mine

    def is_coperta(self, riga: int, colonna: int) -> bool:
        return self._tabellone.is_coperta(riga, colonna)
    

    def __str__(self) -> str:
        result = []
        
        # Intestazione del tabellone iniziale
        result.append("Tabellone iniziale:")
        result.append(str(self.tabellone))  # Stampa il tabellone iniziale
        
        # Aggiungere l'evoluzione della partita
        for i, tabellone in enumerate(self.evoluzione[1:], 1):
            if i-1 < len(self._mosse):  # Controlla se esiste una mossa
                mossa = self._mosse[i-1]  # Ottieni la mossa che ha portato a questo stato
                result.append(f"Tabellone a seguito della mossa di riga {mossa[0]} e colonna {mossa[1]}:")
            else:
                result.append("Tabellone a seguito di una mossa non registrata.")
            result.append(str(tabellone))  # Aggiungi la rappresentazione del tabellone dopo la mossa
        
        return "\n".join(result)

     





def test():
    # Crea una partita con un tabellone 7x7 e 6 mine
    partita = Partita(larghezza=7, altezza=7, n_mine=6)


    # Segna alcune caselle
    partita.segna_casella(2, 3)

    # Scopri una casella sicura
    partita.scopriCasella(4, 4)

    # Scopri una casella con mina
    partita.scopriCasella(0, 0)  # Supponiamo che questa sia una mina
    print(partita)

# Esegui il test
test()
