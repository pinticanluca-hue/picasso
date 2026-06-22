import pygame
import os
import random
import gif_pygame

pygame.init()
pygame.font.init()

# ###############################################################################################################################################################################################
# (quasi) Variabili 
# ###############################################################################################################################################################################################

mazzo_img = []           # mazzo con le immagini delle carte
mazzo_diz = []           # mazzo con i dizionari delle carte
screen_x = 960           # larghezza schermo
screen_y = 540           # altezza schermo
chips = 0                # chips base
moltiplicatore = 0       # moltiplicatore base
grandezza_mano = 8       # grandezza mano base

lista_joker_scorta = []  # Lista di supporto per le immagini caricate
mazzo_joker = []         # Il vero mazzo contenente i DIZIONARI di tutti i Joker completi
joker_posseduti = []     # I Joker attualmente acquistati dal giocatore (INFINITI)
joker_attuale = None     # Il joker estratto nello shop

carte_mano = []          # carte in mano
carte_giocate = []       # carte giocate sul tavolo
carte_selezionate = []   # carte in mano selezionate
boss_hp = 1              # vita boss persa base
boss_hp_full = 1         # vita boss intera base
round_gioco = 1          # round di gioco
visibile = False         # se manitab è visibile
mani = 4                # numero di mani
scarti = 3               # numero scarti
punteggio_mano = "---"   # risultato tra chips e mult
BOSS = "Mattia"
interruttore = False
ante = 0
lista_hp=[300, 800, 2800, 6000, 11000, 20000, 35000, 50000]
# ###############################################################################################################################################################################################
# Definizione di funzioni
# ###############################################################################################################################################################################################

def size(img, bx, by):
    """ Ridimensiona l'immagine mantenendo le proporzioni """
    ix, iy = img.get_size()
    if ix > iy:
        scale_factor = bx / float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        scale_factor = by / float(iy)
        sx = scale_factor * ix
        if sx > bx: 
            scale_factor = bx / float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.scale(img, (int(sx), int(sy)))

def importa_carte_basic():
    global mazzo_img
    mazzo_img = []
    base_path = os.path.dirname(os.path.realpath(__file__))
    for carta in range(1, 53):
        path = os.path.join(base_path, "DEFAULT", "BASIC", f"8BitDeck{carta}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            mazzo_img.append(size(img, 100, 100))

def crea_mazzo_dizionari():
    global mazzo_diz
    mazzo_diz = []
    i = 0
    chips_val = [2,3,4,5,6,7,8,9,10,10,10,10,11]
    numeri = [2,3,4,5,6,7,8,9,10,"jack","queen","king","asso"]
    valori = [2,3,4,5,6,7,8,9,10,11,12,13,14]
    lista_semi = ["cuori", "fiori", "quadri", "picche"]
    
    for seme in lista_semi:
        for valore in valori:
            if i < len(mazzo_img):
                mazzo_diz.append({
                    "seme": seme,
                    "numero": numeri[valore-2],
                    "valore": valore,
                    "chips": chips_val[valore-2],
                    "image": mazzo_img[i],
                    "y": 385,
                    "x": 780,
                    "target_x": 0,
                    "target_y": 385,
                    "stato": "mano"
                })
                i += 1

def scrivi(Scritta, x, y, size_font):
    try:
        my_font = pygame.font.Font("Thin Sans.ttf", size_font)
    except:
        my_font = pygame.font.SysFont("Arial", size_font)
    parola = my_font.render(f"{Scritta}", True, "white")
    screen.blit(parola, (x, y))

def importa_joker_immagini():
    """ Carica le immagini dei joker o crea dei rettangoli di fallback se mancano """
    global lista_joker_scorta
    lista_joker_scorta = []
    
    for joker in range(40):
        try:
            img = size(importa_immagine(f"jokers\joker ({joker+1}).png"), 100,100)

            lista_joker_scorta.append(size(img, 100, 100))
        except:
            pass


def crea_mazzo_joker():
    """ Automatizza la generazione dei 41 Joker unendo la logica alle immagini """
    global mazzo_joker
    mazzo_joker = []
    
    config_joker = [
        ("jolly allegro", "+8 molt se la mano ha una coppia", "mult_mano", 8, "coppia"),
        ("jolly buffo", "+12 molt se la mano ha un tris", "mult_mano", 12, "tris"),
        ("jolly furioso", "+10 molt se la mano ha una doppia coppia", "mult_mano", 10, "doppia coppia"),
        ("jolly folle", "+12 molt se la mano ha una scala", "mult_mano", 12, "scala"),
        ("jolly divertente", "+10 molt se la mnao ha un colore", "mult_mano", 10, "colore"),
        ("mezzo jolly", "+20 chips se la mano ha 3 carte o meno", "chips_limite_carte", 20, 3),
        ("stendardo", "+30 chips per ogni scarto rimasto", "chips_per_scarto", 30, None),
        ("cima mistica", "+15 molt se hai 0 scarti rimasti", "mult_condizionato", 15, "0_scarti"),
        ("err0r3!", "moltiplicatore casuale tra 0 e 25", "mult_random", (0, 25), None),
        ("pugno alzato", "+ il doppio del valore della carta più bassa in mano", "mult_valore_mano", 2, "bassa"),
        ("jolly astratto", "+3 molt per ogni joker posseduto", "mult_per_joker", 3, None),
        ("numeri pari", "+4 molt per ogni numero pari giocato", "mult_per_carta", 4, "pari"),
        ("numeri dispari", "+31 chips per ogni numero dispari giocato", "chips_per_carta", 31, "dispari"),
        ("il duo", "X2 molt se la mano contiene una coppia", "x_mult_mano", 2, "coppia"),
        ("il trio", "X3 molt se la mano contiene un tris", "x_mult_mano", 3, "tris"),
        ("la famiglia", "X4 molt se la mano contiene un poker", "x_mult_mano", 4, "poker"),
        ("l'ordine", "X3 molt se la mano contiene una scala", "x_mult_mano", 3, "scala"),
        ("la tribù", "X2 molt se la mano contiene un colore", "x_mult_mano", 2, "colore"),
        ("fibonacci", "ogni asso, 2, 3, 5 o 8 giocato dà +8 molt", "mult_valori_fibo", 8, [2, 3, 5, 8, 14]),
        ("jolly blu", "+3 chips per ogni carta rimasta nel mazzo", "chips_per_mazzo", 3, None),
        ("jolly subdolo", "+80 chips se la mano ha una coppia", "chips_mano", 80, "coppia"),
        ("jolly astuto", "+100 chips se la mano ha un tris", "chips_mano", 100, "tris"),
        ("jolly intelligente", "+80 chips se la mano ha una doppia coppia", "chips_mano", 80, "doppia coppia"),
        ("jolly infido", "+100 chips se la mano ha uan scala", "chips_mano", 100, "scala"),
        ("jolly furbo", "+80 chips se la mano ha un colore", "chips_mano", 80, "colore"),
        ("faccina", "+5 molt per ogni figura giocata", "mult_per_figura", 5, ["jack", "queen", "king"]),
        ("jolly avido", "ogni carta di quadri dà +3 molt", "mult_seme", 3, "quadri"),
        ("jolly lussurioso", "ogni carta di cuori dà +3 molt", "mult_seme", 3, "cuori"),
        ("jolly iroso", "ogni carta di picche dà +3 molt", "mult_seme", 3, "picche"),
        ("jolly vorace", "ogni carta di fiori dà +3 molt", "mult_seme", 3, "fiori"),
        ("jimbo", "+4 molt sempre", "mult_costante", 4, None)
    ]
    
    for idx, config in enumerate(config_joker):
        nome, testo, tipo, valore, requisito = config
        
        if idx < len(lista_joker_scorta):
            img_joker = lista_joker_scorta[idx]
        else:
            img_joker = lista_joker_scorta[0]
            
        mazzo_joker.append({
            "nome": nome.upper(),
            "testo": testo,
            "tipo_effetto": tipo,
            "valore": valore,
            "requisito": requisito,
            "immagine": img_joker
        })

def importa_immagine(nome):
    base_path = os.path.dirname(os.path.realpath(__file__))
    return pygame.image.load(os.path.join(base_path, nome))

def punteggio(i):
    if not i:
        return [5, 1]
    x = i[0]
    if x == "scala colore": return [100, 8]
    elif x == "poker": return [60, 7]
    elif x == "full": return [40, 4]
    elif x == "colore": return [35, 4]
    elif x == "scala": return [30, 4]
    elif x == "tris": return [30, 3]
    elif x == "doppia coppia": return [20, 2]
    elif x == "coppia": return [10, 2]
    else: return [5, 1]

def attiva_mano(i):
    if len(i) == 0:
        return ["carta alta"]
        
    mano = []
    s_flush = flush = straight = full = poker = two_pair = tris = pair = False
    
    if len(i) == 5:
        s_flush = check_s_flush(i)
        flush = check_flush(i)
        straight = check_straight(i)
        full = check_full(i)
        
    if len(i) >= 4:
        poker = check_poker(i)
        two_pair = check_two_pair(i)
        
    if len(i) >= 3:
        tris = check_tris(i)
        
    if len(i) >= 2:
        pair = check_pair(i)

    if s_flush: mano.append("scala colore")
    if poker: mano.append("poker")
    if full: mano.append("full")
    if flush: mano.append("colore")
    if straight: mano.append("scala")
    if tris: mano.append("tris")
    if two_pair: mano.append("doppia coppia")
    if pair: mano.append("coppia")
    mano.append("carta alta")
        
    return mano

def check_s_flush(i): 
    return check_flush(i) and check_straight(i)

def check_poker(i):
    valori = [x["valore"] for x in i]
    conteggi = {valore: valori.count(valore) for valore in valori}
    return 4 in conteggi.values()

def check_full(i):
    valori = [x["valore"] for x in i]
    conteggi = {valore: valori.count(valore) for valore in valori}
    return 3 in conteggi.values() and 2 in conteggi.values()

def check_flush(i):
    semi = [x["seme"] for x in i]
    return len(set(semi)) == 1

def check_straight(i):
    valori = sorted([x["valore"] for x in i])
    if len(set(valori)) != 5:
        return False
    if valori[4] - valori[0] == 4:
        return True
    if valori == [2, 3, 4, 5, 14]:
        return True
    return False

def check_tris(i):
    valori = [c["valore"] for c in i]
    conteggi = {v: valori.count(v) for v in valori}
    return 3 in conteggi.values()

def check_two_pair(i):
    valori = [c["valore"] for c in i]
    conteggi = {v: valori.count(v) for v in valori}
    valori_conteggi = list(conteggi.values())
    return valori_conteggi.count(2) == 2

def check_pair(i):
    valori = [c["valore"] for c in i]
    conteggi = {v: valori.count(v) for v in valori}
    return 2 in conteggi.values()

def ordinamento(i):
    numeri = [2,3,4,5,6,7,8,9,10,"jack","queen","king","asso"]
    return numeri.index(i["numero"])

def muovi(pos_attuale, pos_finale, velocita):
    return pos_attuale + (pos_finale - pos_attuale) * velocita

# ################################################################################################################################################################# #
# Inizializzazioni e Caricamento Risorse
# ################################################################################################################################################################# #

importa_carte_basic()
crea_mazzo_dizionari()
importa_joker_immagini()
crea_mazzo_joker()

base_path = os.path.dirname(os.path.realpath(__file__))
gif_path = os.path.join(base_path, "boss clown", "jokerboss.gif")
gif_joker = gif_pygame.load(gif_path)

gif_path = os.path.join(base_path, "baltro.backgound.gif")
balatroSfondoGIf = gif_pygame.load(gif_path)

menuinizio = size(importa_immagine("menuinizio.png"), screen_x, screen_y+60)
sfondo = size(importa_immagine("sfondo.png"), screen_x, screen_y)
titolo = size(importa_immagine("titolo.png"), 400, 400)
barra_laterale = size(importa_immagine("colonna laterale ita.png"), screen_x, screen_y)

pulsante_gioca = size(importa_immagine("pulsante gioca.png"), 80, 80)
pulsante_scarta = size(importa_immagine("pulsante scarta.png"), 80, 80)

hp_bar_full = size(importa_immagine("boss clown/hp bar/hp bar full alt.png"), 158, 158)
hp_bar_border = size(importa_immagine("boss clown/hp bar/hp bar border.png"), 158, 158)
hp_bar_red = size(importa_immagine("boss clown/hp bar/hp bar red.png"), 158, 158)

card_back = size(importa_immagine("cards back.png"), 100, 100)

schermata_perso = size(importa_immagine("hai perso.png"), 500, 500)
pulsante_rigioca = size(importa_immagine("pulsante rigioca.png"), 185, 45)
pulsante_menu = size(importa_immagine("pulsante menu.png"), 165, 300)

schermata_vinto = size(importa_immagine("hai vinto.png"), 500, 500)

random.shuffle(mazzo_diz)
random.shuffle(mazzo_joker) 

rettangoli = [
    pygame.Rect(12, 355, 63, 72),  # Tabella combinazioni
    pygame.Rect(12, 438, 63, 72),
    pygame.Rect(410, 490, 80, 40),  # Gioca
    pygame.Rect(550, 490, 80, 40)   # Scarta
]

screen = pygame.display.set_mode((screen_x, screen_y))
clock = pygame.time.Clock()

maniTab = size(importa_immagine("maniPokerBalatropygame.png"), 600, 600)

running = True
starting = True
playing = False
shopping = False
lose = False

# ################################################################################################################################################################# #
# Loop di Gioco Principale
# ################################################################################################################################################################# #

while running:
    clock.tick(60)
    pos = pygame.mouse.get_pos()
    ante = round_gioco // 3
    eventi = pygame.event.get()
    click = False
    for event in eventi:
        if event.type == pygame.QUIT:         
            running = False
            playing = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True

    balatroSfondoGIf.render(screen, (0, 0))

    
    screen.blit(barra_laterale, (0, 0))
    gif_joker.render(screen, (13, 20))
    
    scrivi(chips, 17, 285, 20)
    scrivi(moltiplicatore, 125, 285, 20)
    scrivi(punteggio_mano, 75, 240, 20)
    
    scrivi(BOSS, 94, 405, 20)
    scrivi(ante, 107, 468, 20)
    scrivi(round_gioco, 173, 467, 20)
    scrivi(f"{max(0, boss_hp)} / {boss_hp_full}", 72, 193, 16)
    scrivi(f"{mani}", 100, 355, 20)
    scrivi(f"{scarti}", 170, 355, 20)
    print (pos)
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # Disegna i jolly posseduti (Disposizione a Griglia Infinita)
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    

    if starting:
        screen.blit(menuinizio, (0, -40))
        if click:
            rect_gioca = pygame.Rect(338, 421, 285, 91)
            if rect_gioca.collidepoint(pos):
                starting = False
                playing = True
                boss_hp_full = boss_hp = lista_hp[round_gioco-1]

    if playing:
        screen.blit(pulsante_gioca, (410, 490))
        screen.blit(pulsante_scarta, (550, 490))
        screen.blit(hp_bar_full,(221,21))
        hp_bar_full.fill((160, 6, 213))
        hp_bar_full.blit(hp_bar_red, (0, (int(round(abs((158/(boss_hp_full/boss_hp))-158))))))
        hp_bar_full.blit(hp_bar_border, (0,0))
     

        for joker in joker_posseduti:
            joker_x=260+(((854-260)//len(joker_posseduti))*joker_posseduti.index(joker))
            joker_y=22
            
            screen.blit(joker["immagine"], (joker_x, joker_y))
            
            if len(mazzo_diz) > 0:
                screen.blit(card_back, (780, 385))

        while len(carte_mano) < grandezza_mano and len(mazzo_diz) > 0:
            nuova_carta = mazzo_diz.pop()
            nuova_carta["stato"] = "mano"
            nuova_carta["x"] = 780 
            nuova_carta["y"] = 385
            carte_mano.append(nuova_carta)
            carte_mano.sort(key=ordinamento, reverse=True)

        if click:  
            for i in reversed(carte_mano):
                if i["stato"] == "mano":
                    idx = carte_mano.index(i)
                    y_carta = 360 if i in carte_selezionate else 385
                    x_carta = 285 + (idx * (450 // grandezza_mano))
                    rect_carta = pygame.Rect(x_carta, y_carta, 75, 100)
                    
                    if rect_carta.collidepoint(pos):
                        if i in carte_selezionate:
                            carte_selezionate.remove(i)
                        else:
                            if len(carte_selezionate) < 5:
                                carte_selezionate.append(i)
                        break

        # Logica Pulsante Gioca 
        if click and 0 < len(carte_selezionate) < 6 and rettangoli[2].collidepoint(pos) and mani > 0:
            for vecchia_carta in carte_giocate:
                vecchia_carta["stato"] = "scartata"
                vecchia_carta["target_y"] = 700
            carte_giocate.clear()

            calcolo_mano = attiva_mano(carte_selezionate)
            chips = punteggio(calcolo_mano)[0]
            moltiplicatore = punteggio(calcolo_mano)[1]
            
            # -------------------------------------------------------------------------
            # ENGINE DI ATTIVAZIONE DI TUTTI I JOKER POSSEDUTI
            # -------------------------------------------------------------------------
            for joker in joker_posseduti:
                tipo = joker["tipo_effetto"]
                val = joker["valore"]
                req = joker["requisito"]

                # 1. Effetti basati sul tipo di mano Poker giocata
                if tipo == "mult_mano" and req  in calcolo_mano:
                    moltiplicatore += val
                elif tipo == "chips_mano" and req in calcolo_mano:
                    chips += val
                elif tipo == "x_mult_mano" and req in calcolo_mano:
                    moltiplicatore *= val

                # 2. Effetti costanti e matematici generici
                elif tipo == "mult_costante":
                    moltiplicatore += val
                elif tipo == "mult_random":
                    moltiplicatore += random.randint(val[0], val[1])
                elif tipo == "mult_per_joker":
                    moltiplicatore += val * len(joker_posseduti)
                elif tipo == "chips_per_mazzo":
                    chips += val * len(mazzo_diz)
                elif tipo == "chips_per_scarto":
                    chips += val * scarti
                elif tipo == "mult_condizionato" and req == "0_scarti" and scarti == 0:
                    moltiplicatore += val
                elif tipo == "chips_limite_carte" and len(carte_selezionate) <= req:
                    chips += val

                # 3. Effetti di scansione interna su ogni singola carta giocata
                for carta in carte_selezionate:
                    if tipo == "mult_per_carta":
                        if req == "pari" and isinstance(carta["numero"], int) and carta["numero"] % 2 == 0:
                            moltiplicatore += val
                    elif tipo == "chips_per_carta":
                        if req == "dispari" and isinstance(carta["numero"], int) and carta["numero"] % 2 != 0:
                            chips += val
                    elif tipo == "mult_per_figura" and carta["numero"] in req:
                        moltiplicatore += val
                    elif tipo == "mult_seme" and carta["seme"] == req:
                        moltiplicatore += val
                    elif tipo == "mult_valori_fibo" and carta["valore"] in req:
                        moltiplicatore += val

                # 4. Effetto pugno alzato (valore più basso rimasto in mano)
                if tipo == "mult_valore_mano" and req == "bassa" and carte_mano:
                    valore_minimo = min([c["valore"] for c in carte_mano])
                    moltiplicatore += valore_minimo * val

            for carta in carte_selezionate:
                chips+=carta["chips"]

            # Calcolo finale e riduzione HP
            punteggio_mano = chips * moltiplicatore
            boss_hp -= punteggio_mano
            mani -= 1

            base_x = 430   
            offset = 80    

            for idx, i in enumerate(carte_selezionate):
                i["target_x"] = base_x - 100 + (idx * offset)   
                i["target_y"] = 220
                i["stato"] = "giocata"
                carte_giocate.append(i)
                if i in carte_mano:
                    carte_mano.remove(i)
            
            carte_selezionate.clear()

        # Logica Pulsante Scarta 
        if click and 0 < len(carte_selezionate) < 6 and rettangoli[3].collidepoint(pos) and scarti > 0:
            scarti -= 1
            for i in carte_selezionate:
                i["target_y"] = 700 
                i["stato"] = "scartata"
                if i in carte_mano:
                    carte_mano.remove(i) 
            carte_selezionate.clear()

        if click and rettangoli[0].collidepoint(pos):
            visibile = not visibile

        tutte_le_carte = carte_mano + carte_giocate
        for i in tutte_le_carte:
            if i["stato"] == "mano":
                idx = carte_mano.index(i)
                i["target_x"] = 285 + (idx * (450 // grandezza_mano))
                i["target_y"] = 360 if i in carte_selezionate else 385
            
            i["x"] = muovi(i["x"], i["target_x"], 0.2)
            i["y"] = muovi(i["y"], i["target_y"], 0.2)
            screen.blit(i["image"], (int(i["x"]), int(i["y"])))

        

        if carte_selezionate:
            mano_corrente = attiva_mano(carte_selezionate)
        elif carte_giocate:
            mano_corrente = attiva_mano(carte_giocate)
        else:
            mano_corrente = ["Nessuna"]

        scrivi(mano_corrente[0], 442, 320, 20)
        
        if visibile:
            screen.blit(maniTab, (278, 50))

        if mani <= 0 and boss_hp > 0:
            lose = True
        
        if boss_hp <= 0:
            playing = False
            if len(mazzo_joker) > 0:
                joker_attuale = mazzo_joker.pop()
            shopping = True
            

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # shop
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    if shopping:

        screen.blit(joker_attuale["immagine"], (350, 138)) 
            
        scrivi("HAI OTTENUTO UN NUOVO JOLLY!", 320, 51, 20)
        scrivi(f"{joker_attuale['nome']}", 224, 260, 20)
        scrivi(f"{joker_attuale['testo']}", 224, 317, 20)
            
        kays=pygame.key.get_pressed()
        if kays[pygame.K_SPACE]:
            joker_posseduti.append(joker_attuale)
                
            shopping = False
            playing = True
            round_gioco += 1
            boss_hp_full = boss_hp = round_gioco * 300
            mani, scarti = 4, 3
            punteggio_mano = "---"
            carte_giocate.clear()
            carte_selezionate.clear()
            carte_mano.clear()
            crea_mazzo_dizionari()
            random.shuffle(mazzo_diz)

    if lose:
        screen.blit(schermata_perso, (255, 20))
        screen.blit(pulsante_rigioca, (311, 380))
        screen.blit(pulsante_menu, (540, 380))
        
        rect_rigioca = pygame.Rect(311, 380, 185, 45)  #pos x, pos y, larghezaza bottone, altezza bottone
        rect_menu = pygame.Rect (540, 380, 165, 300)

        if click and rect_rigioca.collidepoint(pos):
            
            # reset valori
            chips = 0
            moltiplicatore = 0
            mani = 4
            scarti = 3
            ante = 1
            round_gioco = 1

            # reset boss
            boss_hp_full = boss_hp = lista_hp[round_gioco-1]

                # svuota carte
            carte_mano.clear()
            carte_giocate.clear()
            carte_selezionate.clear()
            joker_posseduti.clear()

                # ricrea mazzo
            crea_mazzo_dizionari()
            random.shuffle(mazzo_diz)

                # torna nel gioco
            playing = True
            shopping = False
            lose = False

        if click and rect_menu.collidepoint(pos):
            # reset valori
            chips = 0
            moltiplicatore = 0
            mani = 4
            scarti = 3
            ante = 1
            round_gioco = 1

            # reset boss
            boss_hp_full = boss_hp = lista_hp[round_gioco-1]

                # svuota carte
            carte_mano.clear()
            carte_giocate.clear()
            carte_selezionate.clear()
            joker_posseduti.clear()

                # ricrea mazzo
            crea_mazzo_dizionari()
            random.shuffle(mazzo_diz)

                # torna nel gioco
            playing = False
            shopping = False
            lose = False
            starting = True


    pygame.display.flip()

pygame.quit()