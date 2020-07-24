import logging
import json
from aiohttp import web, WSMsgType

from game import Game, GameException


logger = logging.getLogger()


class WSGameUserConnection(web.WebSocketResponse):
    game = None


AWAITING_USERS = []
GAMES = {}


async def commence_game(p1, p2):
    game = Game(p1, p2)
    GAMES[game.uuid] = game

    await p1.send_json({
        'event': 'commencing',
        'uuid': game.uuid,
        'shape': game.players[p1].shape,
        'turn': (p1 is game.turn),
    })

    await p2.send_json({
        'event': 'commencing',
        'uuid': game.uuid,
        'shape': game.players[p2].shape,
        'turn': (p2 is game.turn),
    })


async def handle_ws_connection(request):
    user = web.WebSocketResponse()
    await user.prepare(request)
    logger.debug('Started WS connection')

    if not AWAITING_USERS:
        AWAITING_USERS.append(user)
    else:
        await commence_game(user, AWAITING_USERS.pop(0))

    async for message in user:
        if message.type == WSMsgType.ERROR:
            logger.debug('WS connection closed with exception:', user.exception())
            break

        if message.type == WSMsgType.TEXT:
            try:
                data = json.loads(message.data)
            except json.JSONDecodeError:
                continue

            event = data.get('event', '')
            game_uuid = data.get('uuid', '')
            game = GAMES.get(game_uuid)

            if game is None:
                await user.send_json({'event': 'error', 'message': 'GameDoesNotExist'})
                continue

            if game.players[user].pair.closed:
                try:
                    del GAMES[game_uuid]
                except KeyError:
                    pass
                finally:
                    await user.close()

            try:
                if event == 'turn':
                    x = data.get('x', -1)
                    y = data.get('y', -1)

                    is_game_over = game.handle_turn(user, x=x, y=y)
                    await game.players[user].pair.send_json({
                        'event': 'turn',
                        'x': x,
                        'y': y,
                        'winner': None if is_game_over else (user is not game.winner),
                    })
                elif event == 'unpaired':
                    await user.close()
                    await game.players[user].pair.send_json({'event': 'unpaired'})
                    await game.players[user].pair.close()
            except GameException as exc:
                await user.send_json({'event': 'error', 'message': exc.__class__.__name__})

    logger.debug('WS connection closed')

    return user


# Server message schema
# "event": "commencing" | "turn" | "unpaired" | "error"
#
# {
#   "event": "commencing",
#   "uuid": str,
#   "shape": "x" | "o",
#   "turn": True | False
# }
#
# {
#   "event": "turn",
#   "x": int,
#   "y": int,
#   "winner": True | False | None
# }
#
# {
#   "event": "unpaired"
# }
#
# {
#   "event": "error",
#   "message": str
# }
#
# ===================================================
#
# Client message schema
# "event": "turn" | "unpaired"
#
# {
#   "event": "turn",
#   "uuid": str,
#   "x": int,
#   "y": int
# }
#
# {
#   "event": "unpaired",
#   "uuid": str
# }
#
# {
#   "event": "ack"
# }


app = web.Application()
app.add_routes([web.get('/ws', handle_ws_connection)])


async def prod_app():
    return app


if __name__ == '__main__':
    web.run_app(app)
