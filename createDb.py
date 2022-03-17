"""
CREATE TABLE "currentGiveaways" (
	"giveawayId"	INTEGER UNIQUE,
	"prize"	TEXT,
	"host"	INTEGER,
	"winners"	INTEGER,
	"endTime"	INTEGER,
	"channelId"	INTEGER,
	"buttonId"	INTEGER UNIQUE,
	PRIMARY KEY("giveawayId")
)
"""