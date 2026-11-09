"""Startinhoud: leden en de columns uit de groepsapp (oktober–november 2026)."""

from datetime import date

# (naam, bijnaam, functie, dienstdag 0=ma..6=zo, lid sinds)
MEMBERS = [
    ("Robin", "Ragbin", "Voorzitter", 0, None),
    ("Gijs", None, None, 1, None),
    ("Tygo", None, None, 2, None),
    ("Fien", "Foen de bier", None, 3, date(2026, 10, 9)),
    ("Vincent", None, None, 4, None),
    ("Joffry", "Joffert", None, 5, None),
    ("Erik", None, None, 6, None),
    ("Sammi", None, None, None, date(2026, 10, 12)),
]

COUNTER = {
    "last_incident_date": date(2026, 10, 6),
    "last_incident_text": "Tram ontspoord na aanrijding met bestelbus, Van Baerlestraat (Amsterdam)",
    "sticker_count": 2,
}

# (tijdstip in Europe/Amsterdam, auteur, titel, tekst)
COLUMNS = [
    ("2026-10-10 01:07", "Gijs", "Amsterdam blijft tramongelukken bespaard", """\
Het is vandaag een rustige dag op de Amsterdamse tramrails. Er zijn geen tramongelukken gemeld. De trams kunnen hun routes blijven rijden en reizigers kunnen zich zonder tramongeluknieuws op hun bestemming richten.

De conclusie van vandaag: geen tramongelukken, geen bijzonderheden en hopelijk blijft dat morgen niet zo. 🚋

Tot dinsdag!

EOM"""),
    ("2026-10-10 22:08", "Joffry", "Record aan de pomp", """\
Beste mensen, het is weer zover. Tijd voor de nieuwe update.

Vandaag bleven Amsterdam en haar trammen ook weer buiten het nieuws.

Wel zijn de brandstofprijzen in Nederland weer op een nieuw record! Dat betekent niet alleen dat de wegen minder druk worden, maar ook dat het openbaar vervoer een stuk aantrekkelijker wordt. Houdt daarom komende dagen het nieuws goed in de gaten, want een nieuw Tram Trauma is waarschijnlijk niet ver weg!"""),
    ("2026-10-11 21:10", "Erik", "18 jaar Gouda", """\
Beste TTT'ers! Het is tijd voor de dagelijkse column. Vandaag werden de straten van Amsterdam wederom geteisterd door rust en vrede, er zijn welgeteld 0 (zegge nul) tramongelukken gemeld bij de vrienden van google AI!

Maar niet getreurd! Vandaag is het precies 18 jaar geleden dat het historische Thalys-Intercity ongeluk in Gouda plaatsvond, waar er een Thalys op een Intercity in reed. Daar wordt op geproost!

Houdt moed: het weekend is voorbij, werkend Nederland gaat de straat weer op en de tram weer in. Goede hoop op nieuwe tramongelukken dus!!"""),
    ("2026-10-12 23:30", "Robin", "Amsterdam, epicentrum en tramdsetter", """\
Geachte TTT'ers, mijn dagdienst nadert zijn laatste halte, en de teller staat helaas nog op nul (0).

Iets verder van huis, er is in Rotterdam een auto tegen een tram gebotst, waardoor de tram ontspoord is. Een vergelijkbaar ongeluk in Gent, waarbij een busje op de kant is beland door een botsing met een tram. Beide ongelukken zijn bijna identiek aan een ongeval dat 6 dagen geleden in Amsterdam is gebeurd. Ik denk dat we hierdoor nog kunnen stellen dat Amsterdam naast een tramdsetter (trendsetter) ook nog wel het epicentrum van tramongelukken is.

Als jullie voorzitter roep ik jullie aan om de moed te houden. De vierdaagse tramstilte in de Amsterdamse media is niet voor ons allemaal even makkelijk. Daarom loof ik een biertje uit aan de eerste die een legitiem tramongeluk logt, en dus een sticker plakt.

Opnieuw, houd moed, makkelijkere tijden liggen in het verschiet.

EOM"""),
    ("2026-10-14 02:35", "Gijs", "De stilte is tijdelijk", """\
Geachte TTT'ers,

Mijn dagdienst bereikt zijn laatste halte, en wederom moet ik constateren dat de teller op een teleurstellende nul (0) blijft steken. Een nieuwe dag, een nieuwe stilte, en helaas nog altijd geen stickerwaardige tramincidenten in de hoofdstad.

Houd moed, TTT'ers. De stilte is tijdelijk, de traditie is eeuwig.

EOM"""),
    ("2026-10-15 00:33", "Tygo", "Utrecht zet zichzelf buiten spel", """\
Geachte TTT'ers,

Mijn dagdienst nadert zijn laatste halte, en wederom moet ik constateren dat de teller op nul (zegge 0) blijft steken. Vandaag is het geen stilte door gebrek aan tramwerk, maar door een landelijke staking in het streekvervoer.

Utrecht is het grootste slachtoffer van de dag. Tram 20 en tram 22 rijden vandaag niet, en tram 21 rijdt alleen als er genoeg bestuurders beschikbaar zijn. Een tram die niet rijdt, kan ook niet aangereden worden, aldus Johan Cruyff. ⚽️ Utrecht zet zichzelf vandaag letterlijk buiten spel.

Bij onze grote steden is het dagelijks werk wel gewoon doorgegaan. De trams van GVB en HTM rijden vandaag, en bij de RET rijden de trams en metro's ook. Amsterdam, Den Haag en Rotterdam draaien dus een volledige dienst. Toch kom ik niet verder dan een teller van nul. Rails, trams en spits zijn er volop, alleen het ongeluk blijft uit.

Dat betekent dus ook dat de kelder niet bestickerd gaat worden. Wellicht zien wij morgen een veel drukkere dag, een dag zonder stakingen, een dag met meer trams door de straten. 🚃❌

Morgen moeten we het dan ook hebben van de niet oplettende toeristen, de fietsers die kleurenblind zijn en de Tesla's die niet kunnen wachten op een slagboom, want het wordt morgen een mooie nazomerse dag 🌤. Met temperaturen wisselend tussen 12 graden in de morgen, tot een piek van 19 graden rond borreltijd. Een rustige zuidelijke wind met een kracht van 3 maakt dit alsnog wel truienweer, maar wellicht wel zonder jas erbij.

Dit was het weer weer, en ook weer voor mij. Hopelijk houden jullie moed, want morgen is er weer een dag. Slaap lekker allemaal, oogjes dicht, snaveltjes toe, en kusjes van mij ❤️"""),
    ("2026-10-15 21:49", "Fien", "Wat moet gebeuren zal gebeuren", """\
Hoi goons,

Vandaag wederom een teleurstellende dag. Zo was de opkomst bij de borrel teleurstellend, zo was het aantal tramongelukken in Amsterdam teleurstellend.

Echter, ik heb gemerkt dat wachten op een gebeurtenis die gebeurtenis vaak uitstelt. Misschien moeten we daarom minder hoge verwachtingen hebben voor onze prachtige stickermuur. Wat moet gebeuren zal gebeuren, op zijn tijd. Voor vandaag is Amsterdam vrij gebleven van tramgerelateerde incidenten, maar dit zal niet altijd zo zijn.

Morgen is een nieuwe dag. Misschien de laatste dag van de week, maar absoluut niet de laatste dag van onze rit.

Sorry voor dit (gebrek aan) nieuws.

Er wordt op het moment bijzonder veel water over mij heen gegooid dus ik durf niet meer te typen.

Zet hem op"""),
    ("2026-10-18 00:36", "Joffry", "De moed zakt in de schoenen", """\
Beste TTT'ers,

Graag wil ik even eerlijk zijn over de komende situatie: de moed begint me in de schoenen te zinken. Na een aardige tijd zonder nieuws om over te schrijven, kan men het vertrouwen gaan verliezen. Ik vrees dat dit bij mij een begin aan het maken is.

Desondanks weet ik dat ik er niet alleen voor sta in deze strijd. Met het trouwe team van TTT'ers staan we net zo sterk als de fietsers, auto's of blaadjes die de trams doen ontsporen. Samen met dit team blijven we doorzetten en zullen we ons niet tegen laten houden!

Houd moed!"""),
    ("2026-10-19 08:20", "Erik", "ADE in aantocht", """\
Beste reizigers, na een gebrekkige week ben ik bang dat de stilte nog niet is doorbroken. Gisteren zijn er wederom geen trammen ontspoord, gebotst of zoekgeraakt. Het lijkt erop dat Amsterdam een ware 'veilige tramsituatie' teistert.

Wel begint deze week het langverwachte ADE! Dat betekent onwetende internationals die op alle verkeerde manieren gebruik zullen maken van het volgens hen uiterst ingewikkelde tramnetwerk van regio Amsterdam. Hopelijk zorgen zij voor enerverende tramervaringen en wordt de stilte van afgelopen week de komende dagen gecompenseerd."""),
    ("2026-10-20 12:05", "Robin", "Twee koplampen in de verte", """\
Beste loggers, ik heb jammer genoeg Eriks voorbeeld gevolgd en ben mijn log vergeten. We hebben wederom niks gemist in deze donkere dagen.

Maar ik heb een visie: ik zie twee koplampen aankomen, en ik hoor in de verte een dof getingel. Binnenkort zal er een reiziger van een ver land geschept worden door onze gerailde vervoerstuigen.

EOM"""),
    ("2026-10-20 23:03", "Gijs", "De Siemens Combino wacht", """\
Dappere TTT'ers,

Wederom blijft het compleet stil op het Amsterdamse front. Helaas telde de dag van vandaag (weer!) nul (0) ontsporingen, aanrijdingen of vergelijkbaar tramalant.

Toch vraag ik jullie moed te houden met zicht op het oh zo mooie ADE. Zoals eerder benoemd zijn de uitheemse machten eindelijk begonnen met hun infiltratie van vervelende toeristen achter onze Amsterdamse linies. Deze buitenlandse dwazen komen (te) enthousiast bewapend met zeer zwaar geschut en zullen dus vroeg of laat, dronken of strak, kennismaken met de onverbiddelijke Siemens Combino type 13G (lengte: 29,2 meter, bouwjaar: 2002–2004). En dat zullen we vieren!

EOM"""),
    ("2026-10-22 01:12", "Tygo", "Glad wegdek, verkeerde plek", """\
Geachte TTT'ers,

Mijn dagdienst bereikt zijn laatste halte, en wederom moet ik constateren dat de teller op een teleurstellende nul (0) blijft steken. Ook vandaag worden er in Amsterdam, Rotterdam, Den Haag en Utrecht geen tramongelukken gemeld. Het laatste incident is de aanrijding tussen een auto en een tram op de Groene Hilledijk in Rotterdam, en die ligt alweer negen dagen achter ons.

De omstandigheden zijn nochtans gunstig. Elders in het land veroorzaakt gladheid vanochtend een frontale botsing tussen twee voertuigen op de Wesselseweg in Barneveld, waarbij beide bestuurders lichtgewond raken. Voor de tramwereld is dat net te ver van de rails, want Barneveld heeft geen tram. Maar het bewijst dat het wegdek vandaag glad en onvoorspelbaar is, en zo'n dag is precies wat een tram nodig heeft.

Tot nu toe blijft het bij een rustige dag op de Nederlandse trambanen. Geen ontsporing, geen bestelbus die te laat remt, geen auto die achteruitrijdt op een kruising, geen ADE'ers die voor de trams springen, geen toeristen die overrompeld raken door de drukte, en geen yuppenskelters en kinderbrommers die denken dat ze alleen op de wereld zijn. De trams rijden gewoon hun route en reizigers komen netjes aan op hun bestemming. Het is een rustige dag, maar niet een waarop iemand een sticker plakt.

Houd moed, TTT'ers. De stilte is tijdelijk, de traditie is eeuwig. ❤️"""),
    ("2026-10-23 20:41", "Vincent", "Stormachtige stadsslakken", """\
Beste tellers,

Het spijt me te moeten zeggen dat er op deze stormachtige dag wederom geen ongelukken hebben plaatsgevonden met onze welbekende witblauwe stadsslakken. Er is dus nog geen eind gekomen aan deze droevige komkommertijd.

Maar houd moed! Er zijn vanavond meerdere bomen omgevallen, waarvan één zelfs schade heeft toegebracht aan de tramleiding. Met het noodweer dit weekend is het zeker niet uit te sluiten dat er nieuwe ongelukken op de loer liggen…

EOM"""),
    ("2026-10-25 03:44", "Joffry", "Vastgereden in Den Haag", """\
Goede (late) avond,

Na een week vol tentamens is de druk er weer een beetje af. Daarnaast wil ik wel met treurnis mededelen dat het nogmaals niet gelukt is om de teller omhoog te krijgen.

Wel zie ik dat er in Nederland hard gewerkt wordt om hier verandering in te brengen. Zo schrijft Omroep West dat een automobilist zich vrijdagavond in Den Haag heeft vastgereden op een tramspoor, waardoor tramlijn 4 via een andere route moest rijden.

Het doet mij goed om te zien dat er meerdere acties worden ondernomen en dat er pogingen worden gedaan!

Voor nu hoop ik dat het verzetten van de klok genoeg onrust zaait, zodat wij hier binnenkort weer zege kunnen vieren!

EOM"""),
    ("2026-10-26 22:13", "Robin", "Oproep tot de eerste vergadering", """\
De columntrein van vandaag start zijn rit iets vroeger dan normaal, maar laten we maar gelijk tot het punt komen. Er is vandaag helaas geen tramongeluk gebeurd, en ik denk dat het tijd is voor onze eerste echte officiële vergadering.

We moeten even aan de ronde tafel zitten, want zoals een wijs man zei: "wat een smerige benarde kanker situatie is dit." Dus daarom vraag ik of jullie de LettuceMeet willen invullen.

Wees gerust, dit is niet om aan te kondigen dat de TTT-commune zal vervallen. Juist het tegenovergestelde: ondanks James Joule's wet van energiebehoud geloof en weet ik dat wij tijdens deze donkere tijden de groepsenergie kunnen verhogen en de dynamiek weer gestimuleerd krijgen door elkaar even face-to-face te zien.

Houd moed (en vul in) TTT'ers."""),
    ("2026-10-27 22:21", "Gijs", "Misschien morgen", """\
Beste TTT'ers,

Vandaag deel ik jullie met enige spijt mee dat er geen peuters voor een tram over hun veters zijn gestruikeld. Ook zijn er geen opgefokte UPS-busjes geschept onderweg naar een locatie waar ze toch niet langer dan 3 milliseconden voor de deur wachten, zijn er geen demente omaatjes vergeten dat het tramspoor geen stoep is, is er geen fatbike 'per ongeluk' kneiterhard op de rails geknikkerd, heeft er geen kneusje als statement zijn of haar kleine teen vastgelijmd aan de trambaan, en heeft er geen kleurenblind persoon gezworen dat het stoplicht toch echt op paars stond 😢.

Misschien morgen.

EOM"""),
    ("2026-10-29 00:58", "Tygo", "Proost op IJburg", """\
Geachte TTT'ers,

Mijn dagdienst bereikt zijn laatste halte, en wederom moet ik constateren dat de teller op een teleurstellende nul (0) blijft steken. Ook vandaag blijven Amsterdam, Rotterdam, Den Haag en Utrecht verstoken van stickerwaardig tramnieuws. De trams rijden, de reizigers reizen en de media zwijgen.

Gelukkig is er iets om op te proosten. Vandaag is het precies twee jaar geleden dat in Amsterdam tram 26 op de IJburglaan ontspoorde na een aanrijding met een personenauto. Een toonbeeld van hoe het hoort, en een eerbetoon aan IJburg dat we vandaag met een biertje vieren.

Voor nu is het oogjes dicht, en snaveltjes toe ❤️"""),
    ("2026-10-30 02:22", "Fien", "Licht aan het einde van de tunnel", """\
Vrienden van de TTT,

Helaas vandaag weer een nietszeggende dag. De teller blijft wederom op nul staan, zelfs al hopen we zo op een verandering in het getij.

Ik moet toegeven dat ik, toen ik enkele minuten geleden naar huis aan het fietsen was, even het licht aan het einde van de tunnel dacht te zien. De onmiskenbare tramtoeter gierde me om de oren terwijl een toeterende auto op enkele centimeters na zijn lot ontliep. Jazeker vrienden, ik stond bijna naast het eerste tramgerelateerde ongeluk in tijden. Maar helaas zijn onze burgerrupsen te goed ontworpen en doen de remmen het dusdanig fijn.

Volgende keer hebben we hem."""),
    ("2026-10-30 22:28", "Vincent", "Duimen voor Halloween", """\
Geachte tellers,

Vandaag helaas weer een kort bericht zonder nieuws. Noch tram noch trauma in het nieuws vandaag, wat betekent dat we al sinds begin deze maand geen tram(on)gelukken hebben meegemaakt.

Laten we morgen, op de laatste dag van oktober, duimen dat een dronken halloweenganger denkt dat de tramrails daar voor decoratie ligt, zodat we deze maand mooi afsluiten.

EOM"""),
    ("2026-10-31 23:50", "Joffry", "Een griezelloze avond", """\
Beste TTT'ers,

Op deze spannende en misschien wel enge Halloweenavond blijft het voor de trams in Amsterdam een griezelloze avond.

Ondanks de veelbelovende rellen en chaos, samen met dit schrikfestijn, beloofde dit een avond te worden waarop de teller een stapje vooruit zou gaan. Maar niets is minder waar. Zelfs met al deze gunstige omstandigheden blijven de trams sterk en vastberaden.

Dus laten wij dat dan ook maar doen!

EOM"""),
    ("2026-11-03 23:54", "Gijs", "Een bestuur is geboren", """\
Trots nieuw bestuur van de Trauma Tram Tellers (en Tygo),

Met veel vreugde schrijf ik ongeveer 10 uur na onze geboorte als volwaardig bestuur deze column, met de boodschap dat er weer geen ongelukken zijn gebeurd vandaag. Wel is er vandaag een tram gedoopt tot "rail god" (beetje vreemd, maar ik zie de visie).

Houd moed: naast een dof getingel in de verte is er ook een bestuursfoto, COBO, eigen domein, eigen stickers, eigen app en een eigen community op komst!

Ook wil ik jullie wijzen op de volgende definitie, waarop ik stuitte toen ik voor de lol mijn Engelse woordenboek weer eens doorlas vandaag: "Manifesting is the practice of using mental techniques—such as positive visualization, goal-setting, and affirmations—to imagine achieving a specific desire, based on the belief that focusing your mindset makes that outcome more likely to happen."

Misschien iets voor ons.

Wens me succes met de laatste paar ogenblikken van het nieuws refreshen, en moge er morgen (of vandaag nog 🙏) weer eens een ongeluk gebeuren.

EOM"""),
    ("2026-11-05 13:27", "Tygo", "Een jaar na de Constantijn Huygensstraat", """\
Geachte TTT'ers,

Mijn dagdienst bereikt zijn laatste halte, wellicht met een kleine vertraging door ziekte, en wederom moet ik constateren dat de teller op een teleurstellende nul (0) blijft steken. Ook vandaag zijn er in Amsterdam, Rotterdam, Den Haag en Utrecht geen tramongelukken gemeld. De trams rijden, de reizigers reizen en de media zwijgen.

Gelukkig is er iets om op te proosten. Precies een jaar geleden, op 4 november 2025, botsten een auto en een tram op de Eerste Constantijn Huygensstraat in Amsterdam-West, en twee inzittenden gingen naar het ziekenhuis. Een jaar later staat de teller nog altijd op nul en liggen er een bestuursfoto, een eigen domein en stickers in het verschiet. Dat het toen kon, bewijst dat het ook nu weer kan.

Wel is dit de laatste ochtend voor de grote dag. Vanavond trekken we business casual, colbert aan en een fles op de bar zodat niemand vijftig shots hoeft te halen. De tram moet dus ook morgen zijn rol spelen. Een bestuur dat net is geboren verdient een eerste ongeluk, al is het maar een kleintje."""),
    ("2026-11-05 23:58", "Fien & Sammi", "110 jaar Kinkerstraat", """\
Hoiiiiii TTT'ers,

Vandaag helaas geen ongelukken of zoiets, maar wees niet getreurd.

Het is namelijk exact 110 jaar geleden dat een zesjarig jongetje op de Kinkerstraat 's middags op een rijdende tram van lijn 17 wilde springen. Helaas verloor hij destijds zijn grip. Gecondoleerd.

Hopelijk krijgen we binnenkort weer goed nieuws.

Fijne avond,

Sammi en Fien

Doei"""),
    ("2026-11-07 00:02", "Vincent", "Lederhosen en bierpullen", """\
Geachte tellers,

Wederom vandaag geen ongelukken. Ook al zijn er vandaag verscheidene Oktoberfestgangers gespot met lederhosen en bierpullen, is het gelukt om de trams te ontwijken en niet geblesseerd te raken.

Morgen wellicht meer geluk, en prent het je in: hoe langer het duurt dat er geen ongelukken zijn, hoe meer profijt als het wel gebeurt.

EOM, en allemaal geluk op jullie dagen."""),
    ("2026-11-08 00:05", "Joffry", "Uitbrakken na Oktoberfest", """\
Beste TTT'ers,

Vandaag moet ik mededelen dat de teller zich helaas nog op 0 bevindt. Tijdens het uitbrakken van het fantastische Oktoberfest gisteren heb ik helaas niet het genot van een tramongeluk binnen mogen krijgen.

Samen met deze prachtige, groeiende community hoop ik dat deze droge periode spoedig wordt onderbroken en dat de rails zich binnenkort weer eens goed gaan misdragen.

EOM"""),
    ("2026-11-08 21:44", "Erik", "To be, or not to be", """\
Geachte TTT'ers,

Shakespeare schreef: "To be, or not to be, that is the question." Vandaag kozen onze geliefde tramongelukken voor dat laatste: wederom staat de dagteller op 0 (zegge nul). Tot mijn grote spijt moet ik daarom mededelen dat de stilte die wij deze duistere periode meemaken nog niet doorbroken is.

Wel kan ik met trots mededelen dat, vanwege het rode-lijnprotest, tram 12 vanaf klokslag 11:30 niet meer reed en niet één, niet twee, niet drie maar wel 6 trams een aangepaste route hebben genoten. Ook is in de nacht van 7 op 8 november de eerste officiële vorst van het jaar gemeten en liggen er talloze bladeren op de grond vanwege de herfst, hoera! Hopelijk vriezen de tramrails de komende nachten flink vast en faalt er met een beetje geluk een wissel of twee.

Om af te sluiten laat ik u allen achter met een laatste quote van Shakespeare: "I am to wait, though waiting so be hell…". Goede nacht lieve TTT'ers, allen een heerlijke nachtrust gewenst en dat u mag dromen van de prachtigste tramongelukken."""),
    ("2026-11-09 10:24", "Robin", "Museumnacht: de oude tramkarren rijden", """\
Hallo hallo lieve TTT'ers, even een ongewone rubriek.

Afgelopen zaterdag was het Museumnacht, en heeft Amsterdam de oude tramkarren ingezet. Dit is een historisch moment voor ons als groep.

Daarnaast was tijdens de Museumnacht ook het Amsterdamse trammuseum geopend voor publiek, tot laat in de avond. Voor sommigen van ons een speciale avond, voor velen een gemiste kans.

Vanavond natuurlijk de dagelijkse column, dus tot dan!"""),
]
