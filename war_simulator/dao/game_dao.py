
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, ForeignKey, select
from sqlalchemy.orm import relationship
from ..model.game import Game 
from model.vessel import Vessel
from model.player import Player
from model.battlefield import Battlefield
from model.weapon import Weapon
from model.frigate import Frigate
from model.destroyer import Destroyer
from model.cruiser import Cruiser
from model.submarine import Submarine
from model.vessel import Vessel
from model.surface_missile_launcher import SurfaceMissileLauncher
from model.torpedos_launcher import TorpedoLauncher
from model.air_missile_launcher import AirMissileLauncher
from model.weapon import Weapon



engine = create_engine('sqlite:////tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

class GameEntity(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship("PlayerEntity", back_populates="game",cascade="all, delete-orphan")

class PlayerEntity(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("GameEntity", back_populates="players")
    battle_field = relationship("BattlefieldEntity",back_populates="player",uselist=False, cascade="all, delete-orphan")


class BattlefieldEntity(Base):
    __tablename__ = 'battlefield'
    id = Column(Integer, primary_key=True)
    min_x = Column(Integer)
    min_y = Column(Integer)
    min_z = Column(Integer)
    max_x = Column(Integer)
    max_y = Column(Integer)
    max_z = Column(Integer)
    max_power = Column(Integer)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("PlayerEntity", back_populates="battle_field")
    vessel = relationship("VesselEntity",back_populates="battlefield",uselist=False, cascade="all, delete-orphan") 


class VesselEntity(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True)
    coord_x = Column(Integer)
    coord_y = Column(Integer)
    coord_z = Column(Integer)
    hits_to_be_destroyed = Column(Integer)
    type = Column(String)
    battle_field_id = Column(Integer, ForeignKey("battlefield.id"), nullable=False)
    battlefield = relationship("BattlefieldEntity", back_populates="vessel")
    weapon = relationship("WeapondEntity",back_populates="vessels",uselist=False, cascade="all, delete-orphan")


class WeaponEntity(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    ammunitions = Column(Integer)
    range = Column(Integer)
    type = Column(String)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=False)
    vessels = relationship("VesselEntity", back_populates="weapon")
              

class VesselTypes:
    CRUISER = "Cruiser"
    DESTROYER = "Destroyer"
    FRIGATE = "Frigate"
    SUBMARINE = "Submarine"

class WeaponTypes:
    AIRMISSILELAUNCHER = "AirMissileLauncher"
    SURFACEMISSILELAUNCHER = "SurfaceMissileLauncher"
    TORPEDOLAUNCHER = "TorpedoLauncher" 


class GameDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()
    def create_game(self, game: Game) -> int:
        game_entity = map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id
    def find_game(self, game_id: int) -> Game:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return map_to_game(game_entity)

    def create_player(self, player: Player, game_id) -> int:
        player_entity = map_to_player_entity(player, game_id)
        self.db_session.add(player_entity)
        self.db_session.commit()
        return player_entity.id 
    def find_player(self, player_id: int) -> Player:
        stmt = select(PlayerEntity).where(PlayerEntity.id == player_id)
        player_entity = self.db_session.scalars(stmt).one()
        return map_to_player(player_entity)       
    def create_vessel(self, battlefield_id: int, vessel: Vessel) -> int:
        vessel_entity = map_to_vessel_entity(battlefield_id, vessel)
        self.db_session.add(vessel_entity)
        self.db_session.commit()
        return vessel_entity.id 
    def find_vessel(self, vessel_id: int) -> Vessel:
        stmt = select(VesselEntity).where(VesselEntity.id == vessel_id)
        vessel_entity = self.db_session.scalars(stmt).one()
        return map_to_vessel(vessel_entity)     
    


def map_to_game(game_entity: GameEntity): 
    if game_entity is None:
        return None
    game= Game()
    game.id= game_entity.id
    for player_entity in game_entity.players:
        battle_field=Battlefield(player_entity.battle_field.min_x,
                                 player_entity.battle_field.min_y,
                                 player_entity.battle_field.min_z,
                                 player_entity.battle_field.max_x,
                                 player_entity.battle_field.max_y,
                                 player_entity.battle_field.max_z,
                                 player_entity.battle_field.max_power)
        battle_field.id=player_entity.battle_field.id
        battle_field.vessels=map_to_vessels(player_entity.battle_field.vessels)
        player= Player(player_entity.name,battle_field)
        player.id=player_entity.id
        game.add_player(player)
    return game

def map_to_player(player_entity) -> Player:
    name = player_entity.name
    battle_field = map_to_battlefield(player_entity.battle_field)
    player = Player(name, battle_field)
    player.id = player_entity.id
    return player
def map_to_battlefield(battlefield_entity: BattlefieldEntity) -> Battlefield:
    min_x = battlefield_entity.min_x
    max_x = battlefield_entity.max_x
    min_y = battlefield_entity.min_y
    max_y = battlefield_entity.max_y
    min_z = battlefield_entity.min_z
    max_z = battlefield_entity.max_z
    max_power = battlefield_entity.max_power
    battlefield = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z, max_power)
    return battlefield
   
def map_to_vessels(vessel_entities: list[VesselEntity]) -> list[Vessel]:
    vessels: list[Vessel]=[]
    for vessel_entity in vessel_entities:
        weapon= map_to_weapon(vessel_entity.weapon)
        vessel=map_to_vessel(vessel_entity, weapon)
        vessels.append(vessel)
    return vessels
def map_to_weapon(weapon_entity :WeaponEntity) -> Weapon:
    weapon=None
    match weapon_entity.type:
        case WeaponTypes.SURFACEMISSILELAUNCHER():
            weapon = SurfaceMissileLauncher()
            weapon.id= weapon_entity.id
            weapon.range=weapon_entity.range
            weapon.ammunitions=weapon_entity.ammunitions
            return weapon 
        case WeaponTypes.TORPEDOLAUNCHER():
            weapon = TorpedoLauncher()
            weapon.id= weapon_entity.id
            weapon.range=weapon_entity.range
            weapon.ammunitions=weapon_entity.ammunitions
            return weapon 
        case WeaponTypes.AIRMISSILELAUNCHER():
            weapon = AirMissileLauncher()
            weapon.id= weapon_entity.id
            weapon.range=weapon_entity.range
            weapon.ammunitions=weapon_entity.ammunitions
            return weapon 
    return weapon

def map_to_vessel (vessel_entity:VesselEntity) -> Vessel:
    vessel= None
    match vessel_entity.type:
        case VesselTypes.CRUISER:
            vessel= Cruiser(vessel_entity.coord_x, vessel_entity.coord_y,vessel_entity.coord_z)
            vessel.hits_to_br_destroyed= vessel_entity.hits_to_be_destroyed
            vessel.id=vessel_entity.id
            vessel.weapon=Weapon
            return vessel
        case VesselTypes.DESTROYER:
            vessel= Destroyer(vessel_entity.coord_x, vessel_entity.coord_y,vessel_entity.coord_z)
            vessel.hits_to_be_destroyed= vessel_entity.hits_to_be_destroyed
            vessel.id=vessel_entity.id
            vessel.weapon=Weapon
            return vessel
        case VesselTypes.FRIGATE:
            vessel= Frigate(vessel_entity.coord_x, vessel_entity.coord_y,vessel_entity.coord_z)
            vessel.hits_to_be_destroyed= vessel_entity.hits_to_be_destroyed
            vessel.id=vessel_entity.id
            vessel.weapon=Weapon
            return vessel    
        case VesselTypes.SUBMARINE:
            vessel= Submarine(vessel_entity.coord_x, vessel_entity.coord_y,vessel_entity.coord_z)
            vessel.hits_to_be_destroyed= vessel_entity.hits_to_be_destroyed
            vessel.id=vessel_entity.id
            vessel.weapon=Weapon
            return vessel
    return vessel         




def map_to_game_entity(game: Game) -> GameEntity:
    game_entity = GameEntity()
    if game.get_id() is not None:
        game_entity.id = game.get_id()
    for player in game.get_players():
        player_entity = PlayerEntity()
        player_entity.id = player.id
        player_entity.name = player.get_name()
        battlefield_entity = map_to_battlefield_entity(
            player.get_battlefield())
        vessel_entities = \
            map_to_vessel_entities(player.get_battlefield().id,
                                   player.get_battlefield().vessels)
        battlefield_entity.vessels = vessel_entities
        player_entity.battle_field = battlefield_entity
        game_entity.players.append(player_entity)
    return game_entity

def map_to_vessel_entities(battlefield_id: int, vessels: list[Vessel]) \
        -> list[VesselEntity]:
    vessel_entities: list[VesselEntity] = []
    for vessel in vessels:
        vessel_entity = map_to_vessel_entity(battlefield_id, vessel)
        vessel_entities.append(vessel_entity)

    return vessel_entities


def map_to_vessel_entity(battlefield_id: int, vessel: Vessel) -> VesselEntity:
    vessel_entity = VesselEntity()
    weapon_entity = WeaponEntity()
    weapon_entity.id = vessel.weapon.id
    weapon_entity.ammunitions = vessel.weapon.ammunitions
    weapon_entity.range = vessel.weapon.range
    weapon_entity.type = type(vessel.weapon).__name__
    vessel_entity.id = vessel.id
    vessel_entity.weapon = weapon_entity
    vessel_entity.type = type(vessel).__name__
    vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
    vessel_entity.coord_x = vessel.coordinates[0]
    vessel_entity.coord_y = vessel.coordinates[1]
    vessel_entity.coord_z = vessel.coordinates[2]
    vessel_entity.battle_field_id = battlefield_id
    return vessel_entity

def map_to_player_entity(player: Player) -> PlayerEntity:
    player_entity = PlayerEntity()
    player_entity.id = player.id
    player_entity.name = player.name
    player_entity.battle_field = map_to_battlefield_entity(
        player.get_battlefield())
    return player_entity


def map_to_battlefield_entity(battlefield: Battlefield) -> BattlefieldEntity:
    battlefield_entity = BattlefieldEntity()
    battlefield_entity.id = battlefield.id
    battlefield_entity.max_x = battlefield.max_x
    battlefield_entity.max_y = battlefield.max_y
    battlefield_entity.max_z = battlefield.max_z
    battlefield_entity.min_x = battlefield.min_x
    battlefield_entity.min_y = battlefield.min_y
    battlefield_entity.min_z = battlefield.min_z
    battlefield_entity.max_power = battlefield.max_power
    return battlefield_entity

