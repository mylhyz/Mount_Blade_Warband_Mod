Executable usage:
mb_warband_dedicated.exe [-r commands_file] [-m module_name]
-r reads commands from the specified file
-m server starts with the specified module (default is Native)

Sample .txt files contain sets of commands that can be used to initialize and start a dedicated server
Sample .bat files can help you start your servers with one click

Commands are:
add_factions <faction_id/faction_name> <faction_id/faction_name> #adds new factions for team 1 and team 2 to the factions list
add_map <map_id/map_name> #adds a new map to the maps list
allow_changing_mission <1 or 0> #sets if mission can be changed using admin panel or not
allow_renaming_server <1 or 0> #sets if server name can be renamed using admin panel or not
get_add_to_game_servers_list #returns if server is added to game servers list or not
get_auto_team_balance_limit #returns auto team balance threshold
get_ban_voteable #returns if banning a player is voteable or not
get_bot_count <team_no> #returns number of bots the specified team has
get_control_block_direction <control_block_direction_index> #returns control block direction option
get_combat_gold_bonus #returns combat gold bonus ratio
get_combat_speed <combat_speed_value> #returns combat_speedss
get_defender_spawn_count #returns number of respawns allowed for defenders
get_disallow_ranged_weapons #returns if ranged weapons are allowed or not
get_enable_valve_anti_cheat #returns if valve anti cheat is enabled or not
get_factions_list #returns the factions list
get_factions_voteable #returns if factions are voteable or not
get_force_default_armor #returns if players are forced to wear at least the default armor or not
get_friendly_fire #returns if friendly fire is enabled or not
get_friendly_fire_damage_friend_ratio #returns the percentage of damage received by friend when player hits a friend (0-100)
get_friendly_fire_damage_self_ratio #returns the percentage of damage received by self when player hits a friend (0-100)
get_ghost_mode #returns ghost mode option
get_kick_voteable #returns if kicking a player is voteable or not
get_map_time_limit #returns map time limit in minutes
get_maps_list #returns the maps list
get_maps_voteable #returns if maps are voteable or not
get_max_players #returns the maximum number of players that can join the server
get_melee_friendly_fire #returns if melee friendly fire is enabled or not
get_mission #returns the selected mission
get_num_bots_voteable #returns bots upper limit for votes
get_pass #returns login password for a regular player
get_pass_admin #returns login password for admin privilege
get_pass_private #returns login password for a private player
get_player_respawn_as_bot <1 or 0> #returns if players to spawn as bots or not
get_player_banners_allowed #returns if player banners are allowed or not
get_points_gained_for_capturing_flags #returns points gained for capturing flags
get_port #returns the connection port for server
get_randomize_factions #returns whether the factions are randomized or not
get_respawn_period #returns respawn period
get_round_gold_bonus #returns round gold bonus ratio
get_round_max_seconds #returns maximum seconds for round
get_server_ban_list_file <file_name> #returns the ban list file, necessary for multiple servers running at the same folder
get_server_log_folder #returns the log folder, necessary for multiple servers running at the same folder
get_server_name #returns server name displayed at servers list
get_starting_gold #returns starting gold ratio
get_steam_port #returns the communication port for steam
get_team_point_limit #returns team point limit
get_team_points_gained_for_flags #returns the percentage multiplier to team points gained for flags
get_upload_limit #returns upload limit for server
get_valid_vote_ratio #returns the percentage of 'yes' votes required for a poll to get accepted
get_welcome_message #returns welcome message
get_invasion_difficulty #returns invasion difficulty
read_command_file <filename> #reads a chain of commands from a file at the same directory
set_add_to_game_servers_list #sets if server is added to game servers list or not
set_auto_team_balance_limit #sets auto team balance threshold (2-7, 7 for unlimited)
set_ban_voteable #sets banning a player voteable or not
set_bot_count <team_no> <amount> #sets number of bots for the specified team
set_combat_gold_bonus <value> #sets combat gold bonus ratio (0-100)
set_control_block_direction <control_block_direction_index> #sets control block direction: 0=automatic, 1=by mouse movement
set_combat_speed <combat_speed_value> #sets combat_speed: 0=slowest, 2=average 4 = fastest
set_defender_spawn_count <value> #sets number of respawns allowed for defenders (0-6, 0 for unlimited)
set_disallow_ranged_weapons #sets if ranged weapons are allowed or not
set_enable_valve_anti_cheat #sets if valve anti cheat is enabled or not (0-1)
set_factions <faction_id/faction_name> <faction_id/faction_name> #sets the next factions for team 1 and team 2
set_factions_voteable <1 or 0> #sets factions voteable or not
set_force_default_armor <1 or 0> #sets if players are forced to wear at least the default armor or not
set_friendly_fire <1 or 0> #sets if friendly fire is enabled or not
set_friendly_fire_damage_friend_ratio <value> #sets the percentage of damage received by friend when player hits a friend (0-100)
set_friendly_fire_damage_self_ratio <value> #sets the percentage of damage received by self when player hits a friend (0-100)
set_ghost_mode <ghost_mode_index> #sets ghost mode: 0=free, 1=stick to any player, 2=stick to team members, 3=stick to team members' view
set_kick_voteable <1 or 0> #sets kicking a player voteable or not
set_map <map_id/map_name> #sets the next map
set_map_time_limit <value> #sets map time limit in minutes (5-120)
set_maps_voteable <1 or 0> #sets maps voteable or not
set_max_players <amount> <private_amount> #sets the maximum number of players that can join the server
set_melee_friendly_fire <1 or 0> #sets if melee friendly fire is enabled or not
set_mission <mission_id/mission_name> #sets the next mission
set_num_bots_voteable <amount> #sets bots upper limit for votes
set_pass [<password>] #sets login password for a regular player
set_pass_admin [<password>] #sets login password for admin privilege
set_pass_private [<password>] #sets login password for a private player
set_player_banners_allowed <1 or 0> #sets if player banners are allowed or not
set_player_respawn_as_bot <1 or 0> #sets players to spawn as bots or not
set_points_gained_for_capturing_flags <value> #sets points gained for capturing flags (0-10)
set_port <port> #sets the connection port for server
set_randomize_factions <1 or 0> #randomizes the faction results using the factions list
set_respawn_period <value> #sets respawn period
set_round_gold_bonus <value> #sets round gold bonus ratio (0-1000)
set_round_max_seconds <value> #sets maximum seconds for round
set_server_ban_list_file <file_name> #sets the ban list file, necessary for multiple servers running at the same folder
set_server_log_folder <folder_name> #sets the log folder, necessary for multiple servers running at the same folder
set_server_name <server_name> #sets server name displayed at servers list
set_starting_gold <value> #sets starting gold ratio (0-1000)
set_steam_port #sets the communication port for steam
set_team_point_limit <value> #sets team point limit (3-1000)
set_team_points_gained_for_flags <value> #sets the percentage multiplier to team points gained for flags (25-400)
set_upload_limit <limit> #sets upload limit for server
set_valid_vote_ratio #sets the percentage of 'yes' votes required for a poll to get accepted
set_welcome_message #sets welcome message
set_invasion_difficulty #sets invasion difficulty level mode: 0=easy, 1=normal, 2=endless
set_hidden #hides server from the main list, but still allows players to join from Favourites (set_add_to_game_servers_list should be set to '1'): 0=visible 1=hidden
start #starts the mission or jumps to the next mission if there is already a mission running
stats #reports current fps, number of clients etc.