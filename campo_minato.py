from typing import List, Set, Dict, Tuple, Optional
import random
class Tabellone:
    
    def __init__(self, p:'Partita') -> None:
        self.righe: int = p.altezza
        self.colonne: int = p.larghezza
        self.segnate: Set[int] = set()
        self.scoperte: Set[int] = set()
        self.tabella: List[List[str]] = [['C' for _ in range(self.colonne)] 
                                              for _ in range(self.righe)]
        self.mine: Set[int] = set(random.sample(range(self.righe * self.colonne), p.n_mine))
        self.mine_adiacenti_cache: Dict[int, int] = self.get_mine_adiacenti()
        
    @classmethod
    def copia_tabellone(cls, t:'Tabellone') -> 'Tabellone':
        copia = cls.__new__(cls)
        copia.righe = t.righe
        copia.colonne = t.colonne
        copia.tabella = [riga[:] for riga in t.tabella]  # Copia profonda
        copia.mine = t.mine.copy()
        copia.segnate = t.segnate.copy()
        copia.scoperte = t.scoperte.copy()
        copia.mine_adiacenti_cache = t.mine_adiacenti_cache.copy()
        return copia

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tabellone):
            return False
        return (self.righe == other.righe and
                self.colonne == other.colonne and
                self.mine == other.mine and
                self.segnate == other.segnate and
                self.scoperte == other.scoperte)
        
    def segna_casella(self, r: int, c: int) -> None:
        idx: int = self.get_idx(r, c)
        if idx in self.segnate:
            self.segnate.remove(idx) 
        else:
            self.segnate.add(idx)         
         
    def is_segnata(self, r: int, c: int) -> bool:
        return self.get_idx(r, c) in self.segnate 
    
    def scopri_casella(self, r:int, c:int) -> None:
        idx: int = self.get_idx(r, c)
        self.scoperte.add(idx)  
        
    def is_coperta(self, r: int, c: int) -> bool:
        idx: int = self.get_idx(r, c)
        return idx not in self.scoperte

    # metodo aggiuntivo
    def get_mine_adiacenti(self) -> Dict[int, int]:
        adiacenti: Dict[int, int] = {}
        for r in range(self.righe):
            for c in range(self.colonne):
                idx: int = self.get_idx(r, c)
                adiacenti[idx] = self.mine_adiacenti(r, c)
        return adiacenti
    
    def mine_adiacenti(self, r: int, c: int) -> int:
        count: int = 0
        adjacent: List[Tuple[int, int]] = [
            (r + dr, c + dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)
        ]
        for r, c in adjacent:
            if 0 <= r < self.righe and 0 <= c < self.colonne:
                if self.get_idx(r, c) in self.mine:
                    count += 1
        return count
    
    def get_idx(self, r: int, c: int) -> int:
        idx = r  * self.colonne + c 

        return idx

    def calcola_cella(self, idx: int) -> str:
        """Restituisce la rappresentazione della cella, centralizzando i calcoli."""
        if idx in self.scoperte:
            if idx in self.mine:
                return "Z"  # Mines are revealed
            else:
                # Verifica che il dizionario esista
                if idx in self.mine_adiacenti_cache:
                    return str(self.mine_adiacenti_cache[idx] )
                else:
                    return "0"  # No mines around, empty cell
        elif idx in self.segnate:
            return "D" if idx not in self.mine else "Y"  # Marked as flag (D or Y for mine)
        else:
            return "C" if idx not in self.mine else "X"  # Covered, empty or mine

    def __str__(self) -> str:
        result: List[str] = []
        for r in range(self.righe):
            row: List[str] = []
            for c in range(self.colonne):
                idx = self.get_idx(r+1, c+1)
                # Usa la funzione calcola_cella per ottenere il valore della cella
                row.append(self.calcola_cella(idx))
            result.append("".join(row))
        return "\n".join(result)
    
# ——————————————————————————————————————————————————————————————————————————————————————–————   
class Partita:
    def __init__(self, larghezza: int, altezza: int, n_mine: int):
        self._larghezza: int = larghezza
        self._altezza: int = altezza
        self._n_mine: int = n_mine
        self._stato_corrente: int = 0  # 0 -> in corso, 1 -> successo, 2 -> fallimento
        self._tabellone: 'Tabellone' = Tabellone(self)
        self._evoluzione: List['Tabellone'] = [Tabellone.copia_tabellone(self.tabellone)]
        # Dizionario per tracciare le mosse: chiave = mossa_id, valore = (r, c)
        self._mosse: Dict[int, Tuple[int, int]] = {}
        self._mossa_corrente: int = 0
          
    @property
    def larghezza(self) -> int:
        return self._larghezza
    
    @property
    def mosse(self) -> Dict[int, Tuple[int, int]]:
        return self._mosse
    
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
    def stato_corrente(self, valore: int) -> None:
        self._stato_corrente = valore
        if valore == 2:
            print("Game Over! Hai perso.")
        elif valore == 1:
            print("Congratulazioni! Hai vinto!")
            
    @property
    def tabellone(self) -> 'Tabellone':
        return self._tabellone
    
    @tabellone.setter
    def tabellone(self, tab: 'Tabellone') -> None:
        self._tabellone = tab
    
    @property
    def evoluzione(self) -> List['Tabellone']:
        return self._evoluzione
    
    @evoluzione.setter
    def evoluzione(self, valore: list['Tabellone']) -> None:
        self._evoluzione = valore
        
    def _aggiorna_evoluzione(self) -> None:
        if len(self.evoluzione) == 0 or self.evoluzione[-1] != self.tabellone:
            copia_tabellone: 'Tabellone' = self.tabellone.copia_tabellone(self.tabellone)
            self.evoluzione.append(copia_tabellone)

    
    def segna_casella(self, r: int, c: int) -> None:
        if self.stato_corrente != 0:
            raise RuntimeError("La partita non è in corso.")
        if not self._tabellone.is_coperta(r, c):
            raise ValueError("La casella è già scoperta.")
        
        # Aggiungi la mossa al dizionario delle mosse
        self.mosse[self._mossa_corrente] = (r, c)
        self.tabellone.segna_casella(r, c)
        self._aggiorna_evoluzione()
        self._mossa_corrente += 1
            
    def get_casella_segnata(self, r: int, c: int) -> bool:
        return self.tabellone.is_segnata(r, c)

    def scopriCasella(self, r: int, c: int) -> None:
        if self.stato_corrente != 0:
            raise RuntimeError("La partita non è in corso.")
        if self.get_casella_segnata(r, c):
            raise ValueError("La casella è segnata come mina.")
        if not self.tabellone.is_coperta(r, c):
            raise ValueError("La casella è già scoperta.")
            
        idx: int = self.tabellone.get_idx(r, c)
        self.mosse[self._mossa_corrente] = (r, c)
        self._mossa_corrente += 1
        
        if idx in self.tabellone.mine:
            self.tabellone.scopri_casella(r, c)
            self.stato_corrente = 2  # Partita terminata senza successo

        else:
            self._scopri_ricorsivo(r, c)
            self._aggiorna_evoluzione()
            
        # Verifica le condizioni di vittoria
        celle_totali = self.tabellone.righe * self.tabellone.colonne
        num_mine = len(self.tabellone.mine)
        num_celle_scoperte = len(self.tabellone.scoperte)
        # Verifica se tutte le mine sono segnate correttamente
        mine_segnate = len(self.tabellone.segnate)
        
        if mine_segnate == num_mine and num_celle_scoperte == (celle_totali - num_mine):
            self.stato_corrente = 1  # Partita terminata con successo
            print("Vittoria!")
                    
         
        
    
    def get_mine_adiacenti(self, r: int, c: int) -> int:
        idx: int = self.tabellone.get_idx(r, c)
        return self.tabellone.mine_adiacenti_cache[idx]

    def contiene_mina(self, r: int, c: int) -> bool:
        idx: int = self.tabellone.get_idx(r, c)
        return idx in self.tabellone.mine

    def is_coperta(self, riga: int, colonna: int) -> bool:
        return self.tabellone.is_coperta(riga, colonna)

    def __str__(self) -> str:
        result: List[str] = []
        result.append("Tabellone iniziale:")
        result.append(str(self.evoluzione[0])) 
        # Aggiungere l'evoluzione della partita
        for i, tabellone in enumerate(self.evoluzione[1:], 1):
            if i <= len(self.mosse):  
                mossa: tuple[int, int] = self.mosse[i-1]  # Ottieni la mossa che ha portato a questo stato
                result.append(f"Tabellone a seguito della mossa di riga {mossa[0]} e colonna {mossa[1]}:")
            result.append(str(tabellone)) 
        return "\n".join(result)
     
     
    """ Metodi aggiungtivi """
    
    def _scopri_ricorsivo(self, r: int, c: int) -> None:
        if not (0 <= r < self.altezza and 0 <= c < self.larghezza):
            return
        if not self._tabellone.is_coperta(r, c):
            return

        idx: int = self.tabellone.get_idx(r, c)

        self._tabellone.scopri_casella(r, c)
        if self.tabellone.mine_adiacenti_cache[idx] == 0:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.tabellone.righe and 0 <= cc < self.tabellone.colonne:
                    self._scopri_ricorsivo(rr, cc)
                        
    def visualizza_mine(self) -> None:
        for riga in range(self.altezza):
            for colonna in range(self.larghezza):
                if self.contiene_mina(riga, colonna):
                    self.tabellone.scopri_casella(riga, colonna)  
                    # posso anche aggiungere un'altra logica per mostrare le mine in modo visivo
    
    def reset(self) -> None:
        self.stato_corrente: int = 0  # Ripristina lo stato a "in corso"
        self.tabellone = Tabellone(self)  # Crea un nuovo tabellone
        self.evoluzione = [Tabellone.copia_tabellone(self.tabellone)]  # Ripristina l'evoluzione
        self._mosse = {}
        self.mossa_corrente = 0  
    
    def muovi_mossa(self, direzione: str) -> None:
        if self.stato_corrente != 0:
            print("La partita è terminata. Non puoi modificare il tabellone.")
            return
        if direzione == "avanti" and self._mossa_corrente < len(self._evoluzione) - 1:
            self._mossa_corrente += 1
            self._tabellone = Tabellone.copia_tabellone(self._evoluzione[self._mossa_corrente])

        elif direzione == "indietro" and self._mossa_corrente > 0:
            self._mossa_corrente -= 1
            self._tabellone = Tabellone.copia_tabellone(self._evoluzione[self._mossa_corrente])
        else:
            print("Mossa non valida o non disponibile.")
            return
        print(f"Mossa {direzione} eseguita. Stato attuale: {self._mossa_corrente + 1}")

def test():
    partita = Partita(larghezza=8, altezza=5, n_mine=24)
    partita.segna_casella(2, 3)
    partita.scopriCasella(4, 4)
    partita.scopriCasella(1, 1)
    print(partita)
test()