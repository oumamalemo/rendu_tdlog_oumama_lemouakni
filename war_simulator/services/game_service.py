from dao.game_dao import GameDao
from model.game import Game
from dao.game_dao import GameDao, PlayerEntity, WeaponEntity, VesselEntity
from model.battlefield import Battlefield
from model.player import Player
from model.vessel import Vessel
from model.weapon import Weapon

class GameService:
    def __init__(self):
       self.game_dao = GameDao()

    def create_game(self, player_name: str, min_x: int, max_x: int, min_y: int,
    max_y: int, min_z: int, max_z: int) -> int:
      game = Game()
      battle_field = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z)
      game.add_player(Player(player_name, battle_field))
      return self.game_dao.create_game(game)

    def join_game(self, game_id: int, player_name: str) -> bool:
        game = GameDao.find_game(self,game_id)
        player=Player(player_name,battle_field=None)
        
        if player in game.get_players():
            print("le joueur existe déja")
        else:
            game.add_player(player,Battlefield=None) 

    def get_game(self, game_id: int) -> Game:
        game=self.game_dao.find_game(game_id)
        return game

    def add_vessel(self, game_id: int, player_name: str, vessel_type: str,x: int, y: int, z: int) -> bool:
        vessel=VesselEntity(x,y,z,vessel_type)
        game=self.game_dao.find_game(game_id)
        for player in game.get_players():
            if player.get_name()==player_name:     #on cherche d'abord le player dans le game
                espace_joueur=player.get_battlefield 
                vaisseaux_espace_joueur=Battlefield.get_vessels(espace_joueur) # on cherche les vaisseaux qui occupent l'espace joueur
                for vaisseau in vaisseaux_espace_joueur:
                    if vaisseau.get_coordinates()== (x,y,z):
                        print("impossible d'ajouter le vaisseau ici, l'espace est occupé")
                    else:    
                       espace_joueur=Battlefield.add_vessel(vessel)  # on verifie d'abord que l'espace x,y,z est disponible puis on y ajoute le vaisseau
     
     
    def shoot_at(self, game_id: int, shooter_name: str, vessel_id: int, x: int,y: int, z: int) -> bool:
        game=self.game_dao.find_game(game_id) #on verifie le game
        players=game.get_players()
        for p in players:
            if p.get_name==shooter_name: #on verifie le shooter
                espace_joueur=p.get_battlefield()
                vaissaux_espace_joueur=espace_joueur.get_vessels()
                for v in vaissaux_espace_joueur:
                    if v==self.game_dao.find_vessel(vessel_id):#on verifie le vaisseau à utiliser
                        v.fire_at(x,y,z)#on shoot vers l'emplacement indiqué
                 
                           
    def get_game_status(self, game_id: int, shooter_name: str) -> str:
        game=self.game_dao.find_game(game_id) #on verifie le game
        players=game.get_players()
        for p in players:
            if p.get_name()==shooter_name:                # on cherche si notre joueur 
                espace_joueur=p.get_battlefield()
                vaisseaux_espace_joueur=espace_joueur.get_vessels()
                armes=[]
                for v in vaisseaux_espace_joueur:
                    armes.append(v.get_weapon())
                for a in armes:
                    if a.get_ammunitions !=0:
                        return False
                    nbre_ammunition=0 
                    return nbre_ammunition     
                if vaisseaux_espace_joueur is None or nbre_ammunition==0:
                    return "Perdu" # le joueur perd si il n a pas de vaisseau ou s il n apas d'ammunitions
            else:

                espace_joueur=p.get_battlefield()# dans un game y a que deux joueur 
                vaisseaux_espace_joueur=espace_joueur.get_vessels()
                armes=[]
                for v in vaisseaux_espace_joueur:
                    armes.append(v.get_weapon())
                for a in armes:
                    if a.get_ammunitions !=0:
                        return False
                    nbre_ammunition=0 
                    return nbre_ammunition     
                if vaisseaux_espace_joueur is None or nbre_ammunition==0:
                    return "GAGNE"  # si le deuxième joueur perd cela veut dire que le premier= shooter_name a gané     
            return "ENCOURS" # si aucun joueur n a perdu cela signifie que le jeu est en cours
