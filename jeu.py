import pygame
import random
import math
import json
import os

pygame.init()

LARGEUR, HAUTEUR = 1920, 1080
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 0, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
GRIS = (128, 128, 128)
ROSE = (255, 192, 203)
JAUNE = (255, 255, 0)

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Mon Jeu")

class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLEU)
        self.rect = self.image.get_rect()
        self.rect.center = (LARGEUR // 2, HAUTEUR // 2)
        self.vitesse = 5
        self.vie = 100
        self.armure = 0
        self.tir_triple = False

    def deplacer(self, dx, dy):
        self.rect.x += dx * self.vitesse
        self.rect.y += dy * self.vitesse
        self.rect.clamp_ip(ecran.get_rect())

    def tirer(self, pos_souris):
        if self.tir_triple:
            return [
                Projectile(self.rect.centerx, self.rect.centery, pos_souris),
                Projectile(self.rect.centerx, self.rect.centery, (pos_souris[0] + 100, pos_souris[1])),
                Projectile(self.rect.centerx, self.rect.centery, (pos_souris[0] - 100, pos_souris[1]))
            ]
        else:
            return [Projectile(self.rect.centerx, self.rect.centery, pos_souris)]

    def prendre_degats(self, degats):
        if self.armure > 0:
            if self.armure >= degats:
                self.armure -= degats
            else:
                degats_restants = degats - self.armure
                self.armure = 0
                self.vie -= degats_restants
        else:
            self.vie -= degats
        self.vie = max(0, self.vie)

    def soigner(self, soin):
        self.vie = min(self.vie + soin, 100)

    def ajouter_armure(self, armure):
        self.armure = min(self.armure + armure, 200)

    def activer_tir_triple(self):
        self.tir_triple = True

    def desactiver_tir_triple(self):
        self.tir_triple = False

class Ennemi(pygame.sprite.Sprite):
    def __init__(self, type_ennemi='normal'):
        super().__init__()
        self.type_ennemi = type_ennemi
        if type_ennemi == 'special':
            self.image = pygame.Surface((30, 30))
            self.image.fill(BLANC)
            self.vie = 3
            self.vitesse = 1.5
        elif type_ennemi == 'rapide':
            self.image = pygame.Surface((10, 10))
            self.image.fill(ROSE)
            self.vie = 1
            self.vitesse = 4
        elif type_ennemi == 'boss':
            self.image = pygame.Surface((60, 60))
            self.image.fill(ROSE)
            self.vie = 10
            self.vitesse = 2
        else:  # normal
            self.image = pygame.Surface((20, 20))
            self.image.fill(ROUGE)
            self.vie = 1
            self.vitesse = 3
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = random.randint(0, HAUTEUR - self.rect.height)

    def suivre(self, joueur, ennemis):
        dx = joueur.rect.centerx - self.rect.centerx
        dy = joueur.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            nouvelle_position = self.rect.move(dx * self.vitesse, dy * self.vitesse)
            
            collision = False
            for autre_ennemi in ennemis:
                if autre_ennemi != self and nouvelle_position.colliderect(autre_ennemi.rect):
                    collision = True
                    break
            
            if not collision:
                self.rect = nouvelle_position
        
        self.rect.clamp_ip(ecran.get_rect())

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, pos_cible):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(BLANC)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vitesse = 10
        dx = pos_cible[0] - x
        dy = pos_cible[1] - y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.vx = (dx / dist) * self.vitesse
            self.vy = (dy / dist) * self.vitesse
        else:
            self.vx = self.vy = 0

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if not ecran.get_rect().colliderect(self.rect):
            self.kill()

class Bonus(pygame.sprite.Sprite):
    def __init__(self, type_bonus):
        super().__init__()
        self.type = type_bonus
        self.image = pygame.Surface((20, 20))
        if type_bonus == 'soin':
            self.image.fill(VERT)
        elif type_bonus == 'bouclier':
            self.image.fill(GRIS)
        elif type_bonus == 'tir_triple':
            self.image.fill(JAUNE)
        pygame.draw.circle(self.image, self.image.get_at((0, 0)), (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = random.randint(0, HAUTEUR - self.rect.height)

def charger_scores():
    if os.path.exists('scores.json'):
        with open('scores.json', 'r') as f:
            return json.load(f)
    return []

def sauvegarder_scores(scores):
    with open('scores.json', 'w') as f:
        json.dump(scores, f)

def afficher_menu():
    ecran.fill(NOIR)
    font = pygame.font.Font(None, 36)
    titre = font.render("Mon Jeu", True, BLANC)
    jouer = font.render("Appuyez sur ESPACE pour jouer", True, BLANC)
    quitter = font.render("Appuyez sur Q pour quitter", True, BLANC)
    ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, HAUTEUR // 4))
    ecran.blit(jouer, (LARGEUR // 2 - jouer.get_width() // 2, HAUTEUR // 2))
    ecran.blit(quitter, (LARGEUR // 2 - quitter.get_width() // 2, HAUTEUR * 3 // 4))
    
    scores = charger_scores()
    if scores:
        meilleurs_scores = sorted(scores, reverse=True)[:5]
        y = HAUTEUR // 2 + 50
        for i, score in enumerate(meilleurs_scores, 1):
            texte = font.render(f"{i}. {score}", True, BLANC)
            ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, y))
            y += 30
    
    pygame.display.flip()

def afficher_pause():
    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    ecran.blit(overlay, (0, 0))
    font = pygame.font.Font(None, 36)
    pause = font.render("PAUSE", True, BLANC)
    reprendre = font.render("Appuyez sur ESPACE pour reprendre", True, BLANC)
    quitter = font.render("Appuyez sur Q pour quitter", True, BLANC)
    ecran.blit(pause, (LARGEUR // 2 - pause.get_width() // 2, HAUTEUR // 4))
    ecran.blit(reprendre, (LARGEUR // 2 - reprendre.get_width() // 2, HAUTEUR // 2))
    ecran.blit(quitter, (LARGEUR // 2 - quitter.get_width() // 2, HAUTEUR * 3 // 4))
    pygame.display.flip()

def afficher_resume(score, vague):
    ecran.fill(NOIR)
    font = pygame.font.Font(None, 48)
    titre = font.render("Fin de la partie", True, BLANC)
    score_texte = font.render(f"Score final: {score}", True, BLANC)
    vague_texte = font.render(f"Vague atteinte: {vague}", True, BLANC)
    retour = font.render("Appuyez sur ESPACE pour revenir au menu", True, BLANC)
    
    ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, HAUTEUR // 4))
    ecran.blit(score_texte, (LARGEUR // 2 - score_texte.get_width() // 2, HAUTEUR // 2))
    ecran.blit(vague_texte, (LARGEUR // 2 - vague_texte.get_width() // 2, HAUTEUR * 5 // 8))
    ecran.blit(retour, (LARGEUR // 2 - retour.get_width() // 2, HAUTEUR * 3 // 4))
    
    scores = charger_scores()
    scores.append(score)
    sauvegarder_scores(scores)
    
    pygame.display.flip()
    
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                attente = False
    return True

def jeu_principal():
    joueur = Joueur()
    tous_sprites = pygame.sprite.Group(joueur)
    ennemis = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    bonus = pygame.sprite.Group()
    
    score = 0
    vague = 1
    horloge = pygame.time.Clock()
    
    en_jeu = True
    en_pause = False
    
    def spawn_vague():
        # Spawn des ennemis (rouges)
        for _ in range(3 * vague):
            ennemis.add(Ennemi('normal'))
        
        # Spawn des ennemis (blancs)
        if vague % 5 == 0:
            for _ in range(vague // 5):
                ennemis.add(Ennemi('special'))
        
        # Spawn des ennemis (roses)
        if vague >= 10:
            nombre_rapides = 2 * ((vague - 10) // 2 + 1)
            for _ in range(nombre_rapides):
                ennemis.add(Ennemi('rapide'))
        
        # Spawn du boss (carré rose)
        if vague >= 20 and (vague - 20) % 10 == 0:
            nombre_boss = (vague - 20) // 10 + 1
            for _ in range(nombre_boss):
                ennemis.add(Ennemi('boss'))
        
        # Spawn des bonus
        if random.random() < 0.10:
            bonus.add(Bonus('soin'))
        if random.random() < 0.05:
            bonus.add(Bonus('bouclier'))
        if random.random() < 0.03:
            bonus.add(Bonus('tir_triple'))
    
    spawn_vague()
    
    while en_jeu:
        horloge.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_pause = not en_pause
            if event.type == pygame.MOUSEBUTTONDOWN and not en_pause:
                if event.button == 1:  # Clic gauche
                    projectiles.add(joueur.tirer(event.pos))
        
        if en_pause:
            afficher_pause()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                return True
            if keys[pygame.K_SPACE]:
                en_pause = False
            continue
        
        keys = pygame.key.get_pressed()
        joueur.deplacer(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                        keys[pygame.K_DOWN] - keys[pygame.K_UP])
        
        for ennemi in ennemis:
            ennemi.suivre(joueur, ennemis)
            if pygame.sprite.collide_rect(ennemi, joueur):
                joueur.prendre_degats(1)
                if joueur.vie <= 0:
                    return afficher_resume(score, vague)
        
        for projectile in projectiles:
            ennemis_touches = pygame.sprite.spritecollide(projectile, ennemis, False)
            for ennemi in ennemis_touches:
                ennemi.vie -= 1
                if ennemi.vie <= 0:
                    ennemi.kill()
                    score += 1
                projectile.kill()

        bonus_collectes = pygame.sprite.spritecollide(joueur, bonus, True)
        for bonus_item in bonus_collectes:
            if bonus_item.type == 'soin':
                joueur.soigner(100)
            elif bonus_item.type == 'bouclier':
                joueur.ajouter_armure(200)
            elif bonus_item.type == 'tir_triple':
                joueur.activer_tir_triple() 
        
        if len(ennemis) == 0:
            vague += 1
            spawn_vague()
            joueur.desactiver_tir_triple()
        
        tous_sprites.update()
        projectiles.update()
        
        ecran.fill(NOIR)
        tous_sprites.draw(ecran)
        ennemis.draw(ecran)
        projectiles.draw(ecran)
        bonus.draw(ecran)
        
        font = pygame.font.Font(None, 36)
        texte_score = font.render(f"Score: {score}", True, BLANC)
        texte_vie = font.render(f"Vie: {joueur.vie}", True, BLANC)
        texte_armure = font.render(f"Armure: {joueur.armure}", True, BLANC)
        texte_vague = font.render(f"Vague: {vague}", True, BLANC)
        ecran.blit(texte_score, (10, 10))
        ecran.blit(texte_vie, (10, 50))
        ecran.blit(texte_armure, (10, 90))
        ecran.blit(texte_vague, (10, 130))
        
        pygame.display.flip()

def main():
    en_cours = True
    while en_cours:
        afficher_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    jeu_principal()
                elif event.key == pygame.K_q:
                    en_cours = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
