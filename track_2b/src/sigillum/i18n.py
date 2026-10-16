"""Texts of the seal. Report texts in English and French; the plain-language
verdict in the four national languages plus English.

The plain-language lines below are *fallback templates*, used when Apertus is
not reachable. When Apertus is available it rewrites them (see explain.py);
each rewritten line must still cite the evidence it rests on.
Romansh templates: Rumantsch Grischun, to be proof-read by a native speaker.
"""

LANGS = ("fr", "de", "it", "rm", "en")

GRADE_LABEL = {
    "A": {"en": "Fully sovereign", "fr": "Pleinement souverain", "de": "Vollständig souverän", "it": "Pienamente sovrano", "rm": "Cumplainamain suveran"},
    "B": {"en": "Largely sovereign", "fr": "Largement souverain", "de": "Weitgehend souverän", "it": "Ampiamente sovrano", "rm": "Per gronda part suveran"},
    "C": {"en": "Partial or unproven", "fr": "Partiel ou non prouvé", "de": "Teilweise oder unbewiesen", "it": "Parziale o non dimostrato", "rm": "Parzial u betg cumprovà"},
    "D": {"en": "Foreign dependencies", "fr": "Dépendances étrangères", "de": "Ausländische Abhängigkeiten", "it": "Dipendenze estere", "rm": "Dependenzas da l'exteriur"},
    "E": {"en": "Dependent on foreign services", "fr": "Dépendant de l'étranger", "de": "Vom Ausland abhängig", "it": "Dipendente dall'estero", "rm": "Dependent da l'exteriur"},
}

QUESTION = {
    1: {"en": "Where does the model live?", "fr": "Où vit le modèle ?", "de": "Wo läuft das Modell?", "it": "Dove vive il modello?", "rm": "Nua viva il model?"},
    2: {"en": "Where does the data go?", "fr": "Où vont les données ?", "de": "Wohin gehen die Daten?", "it": "Dove vanno i dati?", "rm": "Nua van las datas?"},
    3: {"en": "What happens without internet?", "fr": "Que se passe-t-il sans internet ?", "de": "Was passiert ohne Internet?", "it": "Cosa succede senza internet?", "rm": "Tge capita senza internet?"},
    4: {"en": "Who else is in the loop?", "fr": "Qui d'autre est dans la boucle ?", "de": "Wer ist sonst noch beteiligt?", "it": "Chi altro è coinvolto?", "rm": "Tgi è anc participà?"},
    5: {"en": "Can it be verified?", "fr": "Peut-on le vérifier ?", "de": "Lässt es sich prüfen?", "it": "Si può verificare?", "rm": "Sa lascha quai verifitgar?"},
}

UNKNOWN = {"en": "unknown", "fr": "inconnu", "de": "unbekannt", "it": "sconosciuto", "rm": "nunenconuschent"}

# ---------------------------------------------------------------------------
# Reasons (report body) — en / fr
# ---------------------------------------------------------------------------
REASON = {
    "Q1_CLOSED_FOREIGN": {"en": "A closed model is called at a foreign provider: {hosts}.", "fr": "Un modèle fermé est appelé chez un fournisseur étranger : {hosts}."},
    "Q1_OPEN_FOREIGN": {"en": "An open model is served by a foreign inference provider: {hosts}.", "fr": "Un modèle ouvert est servi par un fournisseur d'inférence étranger : {hosts}."},
    "Q1_CLOSED_NAME": {"en": "A closed model is referenced ({models}); its host cannot be under the organisation's control.", "fr": "Un modèle fermé est référencé ({models}) ; son hébergement échappe à l'organisation."},
    "Q1_SWISS": {"en": "The model endpoint is operated in Switzerland: {hosts}.", "fr": "Le point d'accès du modèle est opéré en Suisse : {hosts}."},
    "Q1_LOCAL": {"en": "An open-weight model is served on the organisation's own machine ({serving}).", "fr": "Un modèle à poids ouverts est servi sur la machine de l'organisation ({serving})."},
    "Q1_CONFIGURABLE": {"en": "The model endpoint is configurable, but no local serving recipe ships with the project: location depends on deployment.", "fr": "Le point d'accès du modèle est configurable, mais aucune recette de service local n'est fournie : l'emplacement dépend du déploiement."},
    "Q1_CLAIM_ONLY": {"en": "The documentation says the model runs locally; no trace in the code confirms it. Claim without proof: capped at C.", "fr": "La documentation affirme que le modèle tourne en local ; aucune trace dans le code ne le confirme. Affirmation sans preuve : plafonnée à C."},
    "Q2_CONTENT_FOREIGN": {"en": "User content (prompts, documents) is sent abroad: {hosts}.", "fr": "Le contenu des utilisateurs (questions, documents) part à l'étranger : {hosts}."},
    "Q2_CONTENT_EU": {"en": "User content is sent to a provider in the EU: {hosts}.", "fr": "Le contenu des utilisateurs part chez un fournisseur dans l'UE : {hosts}."},
    "Q2_META_FOREIGN": {"en": "Usage metadata (IP address, pages, events) is sent abroad: {hosts}.", "fr": "Des métadonnées d'usage (adresse IP, pages, événements) partent à l'étranger : {hosts}."},
    "Q2_META_EU": {"en": "Usage metadata is sent to a provider in the EU: {hosts}.", "fr": "Des métadonnées d'usage partent chez un fournisseur dans l'UE : {hosts}."},
    "Q2_UNKNOWN_HOST": {"en": "Data is sent to destinations Sigillum cannot locate: {hosts}.", "fr": "Des données partent vers des destinations que Sigillum ne sait pas situer : {hosts}."},
    "Q2_SWISS_ONLY": {"en": "All external destinations are in Switzerland: {hosts}.", "fr": "Toutes les destinations externes sont en Suisse : {hosts}."},
    "Q2_NOTHING_LEAVES": {"en": "No external destination found in {files} code and configuration files.", "fr": "Aucune destination externe trouvée dans {files} fichiers de code et de configuration."},
    "Q2_CLAIM_ONLY": {"en": "The documentation says data stays put; the code gives nothing to check. Capped at C.", "fr": "La documentation affirme que les données restent sur place ; le code ne permet pas de le vérifier. Plafonné à C."},
    "Q3_STOPS": {"en": "The core feature calls a foreign service ({hosts}): without internet, it stops.", "fr": "La fonction principale appelle un service étranger ({hosts}) : sans internet, tout s'arrête."},
    "Q3_CDN": {"en": "Scripts are loaded from a CDN at runtime ({hosts}): offline, the interface breaks.", "fr": "Des scripts sont chargés depuis un CDN à l'exécution ({hosts}) : hors ligne, l'interface casse."},
    "Q3_DOWNLOAD": {"en": "Model weights are downloaded at start-up: the first run needs internet.", "fr": "Les poids du modèle sont téléchargés au démarrage : le premier lancement exige internet."},
    "Q3_FONTS": {"en": "Fonts come from a remote service ({hosts}): offline, the display degrades.", "fr": "Les polices viennent d'un service distant ({hosts}) : hors ligne, l'affichage se dégrade."},
    "Q3_REMOTE_MODEL": {"en": "The model is reached over the network and no local option ships with the project: degraded offline.", "fr": "Le modèle est joint par le réseau et aucune option locale n'est fournie : service dégradé hors ligne."},
    "Q3_OFFLINE_PROVEN": {"en": "A test runs the project with networking disabled.", "fr": "Un test fait tourner le projet avec le réseau coupé."},
    "Q3_OFFLINE_INFERRED": {"en": "Everything runs locally according to the code, but no test runs it offline.", "fr": "D'après le code, tout tourne en local, mais aucun test ne le fait tourner hors ligne."},
    "Q3_CLAIM_ONLY": {"en": "The documentation says it works offline; nothing in the code shows it. Capped at C.", "fr": "La documentation affirme que l'outil marche hors ligne ; rien dans le code ne le montre. Plafonné à C."},
    "Q4_TRACKERS": {"en": "Analytics or tracking services are integrated: {hosts}.", "fr": "Des services d'analyse ou de suivi sont intégrés : {hosts}."},
    "Q4_TELEMETRY_ON": {"en": "{frameworks} collects usage statistics by default and no off-switch was found.", "fr": "{frameworks} collecte des statistiques d'usage par défaut, et aucun interrupteur n'a été trouvé."},
    "Q4_VENDOR": {"en": "A third-party AI vendor sees every request: {hosts}.", "fr": "Un fournisseur d'IA tiers voit chaque requête : {hosts}."},
    "Q4_OPAQUE": {"en": "Some components cannot be audited (binaries, minified bundles or no dependency manifest): unknown.", "fr": "Certains composants ne peuvent pas être audités (binaires, fichiers minifiés ou absence de manifeste de dépendances) : inconnu."},
    "Q4_NONE": {"en": "No analytics, telemetry or third-party AI service found among {deps} declared dependencies.", "fr": "Aucun service d'analyse, de télémétrie ou d'IA tierce parmi {deps} dépendances déclarées."},
    "Q4_CLAIM_ONLY": {"en": "The documentation says there is no tracking; the code gives nothing to check.", "fr": "La documentation affirme qu'il n'y a aucun suivi ; le code ne permet pas de le vérifier."},
    "Q5_NO_SOURCE": {"en": "No source code to examine.", "fr": "Aucun code source à examiner."},
    "Q5_NO_LICENSE": {"en": "No recognised open licence: nobody may reuse or redistribute the code.", "fr": "Aucune licence ouverte reconnue : personne ne peut réutiliser ni redistribuer le code."},
    "Q5_REPRODUCIBLE": {"en": "Open licence ({license}), container build, pinned dependencies and tests: anyone can rebuild and re-check.", "fr": "Licence ouverte ({license}), conteneur, dépendances figées et tests : chacun peut reconstruire et revérifier."},
    "Q5_PARTIAL": {"en": "Open licence ({license}) and a partly reproducible build.", "fr": "Licence ouverte ({license}) et construction en partie reproductible."},
    "Q5_LICENSE_ONLY": {"en": "Open licence ({license}), but no reproducible build.", "fr": "Licence ouverte ({license}), mais aucune construction reproductible."},
}

FIX = {
    "FIX_SERVE_LOCAL": {"en": "Serve Apertus yourself (llama.cpp, vLLM or Ollama) or on Swiss infrastructure, and read the endpoint from LLM_BASE_URL.", "fr": "Servez Apertus vous-même (llama.cpp, vLLM ou Ollama) ou sur une infrastructure suisse, et lisez l'adresse dans LLM_BASE_URL."},
    "FIX_OPEN_MODEL": {"en": "Replace the closed model by an open-weight model such as Apertus.", "fr": "Remplacez le modèle fermé par un modèle à poids ouverts comme Apertus."},
    "FIX_LOCAL_RECIPE": {"en": "Ship a local serving recipe (e.g. a llama.cpp service in docker-compose).", "fr": "Fournissez une recette de service local (par exemple un service llama.cpp dans docker-compose)."},
    "FIX_PROVE_CLAIM": {"en": "Back the claim with code: a serving config, a compose file, a test.", "fr": "Appuyez l'affirmation sur du code : configuration de service, fichier compose, test."},
    "FIX_KEEP_CONTENT": {"en": "Keep user content on infrastructure you control or in Switzerland.", "fr": "Gardez le contenu des utilisateurs sur une infrastructure que vous contrôlez, ou en Suisse."},
    "FIX_SELFHOST_FONTS": {"en": "Serve the fonts from your own server.", "fr": "Servez les polices depuis votre propre serveur."},
    "FIX_VENDOR_SCRIPTS": {"en": "Bundle the scripts with the application instead of loading them from a CDN.", "fr": "Intégrez les scripts à l'application au lieu de les charger depuis un CDN."},
    "FIX_REMOVE_ANALYTICS": {"en": "Remove the analytics service, or self-host an alternative in Switzerland.", "fr": "Retirez le service d'analyse, ou auto-hébergez une alternative en Suisse."},
    "FIX_DOCUMENT_HOSTS": {"en": "Document who operates each destination and where, or remove it.", "fr": "Documentez qui opère chaque destination et où, ou retirez-la."},
    "FIX_BAKE_WEIGHTS": {"en": "Bake the weights into the image or set HF_HUB_OFFLINE=1 after the first download.", "fr": "Intégrez les poids dans l'image, ou fixez HF_HUB_OFFLINE=1 après le premier téléchargement."},
    "FIX_OFFLINE_TEST": {"en": "Add a test that runs the project with networking disabled (docker run --network none).", "fr": "Ajoutez un test qui fait tourner le projet réseau coupé (docker run --network none)."},
    "FIX_TELEMETRY_STREAMLIT": {"en": "Add `[browser] gatherUsageStats = false` to .streamlit/config.toml.", "fr": "Ajoutez `[browser] gatherUsageStats = false` dans .streamlit/config.toml."},
    "FIX_TELEMETRY_GRADIO": {"en": "Set GRADIO_ANALYTICS_ENABLED=False (and never share=True).", "fr": "Fixez GRADIO_ANALYTICS_ENABLED=False (et jamais share=True)."},
    "FIX_TELEMETRY_CHROMA": {"en": "Create the client with Settings(anonymized_telemetry=False).", "fr": "Créez le client avec Settings(anonymized_telemetry=False)."},
    "FIX_TELEMETRY_VLLM": {"en": "Set VLLM_NO_USAGE_STATS=1 and DO_NOT_TRACK=1.", "fr": "Fixez VLLM_NO_USAGE_STATS=1 et DO_NOT_TRACK=1."},
    "FIX_MANIFEST": {"en": "Declare dependencies in a manifest and replace opaque files by their sources.", "fr": "Déclarez les dépendances dans un manifeste et remplacez les fichiers opaques par leurs sources."},
    "FIX_PUBLISH_CODE": {"en": "Publish the source code.", "fr": "Publiez le code source."},
    "FIX_LICENSE": {"en": "Add an open licence (Apache-2.0, MIT, EUPL…).", "fr": "Ajoutez une licence ouverte (Apache-2.0, MIT, EUPL…)."},
    "FIX_TESTS": {"en": "Add automated tests.", "fr": "Ajoutez des tests automatisés."},
    "FIX_PIN": {"en": "Pin dependency versions (lockfile).", "fr": "Figez les versions des dépendances (fichier de verrouillage)."},
    "FIX_CONTAINER": {"en": "Provide a container build (Dockerfile).", "fr": "Fournissez une construction en conteneur (Dockerfile)."},
}

GAP_TAG = {
    "LOCAL_MODEL": {"en": "runs locally", "fr": "tourne en local"},
    "SOVEREIGN": {"en": "sovereign", "fr": "souverain"},
    "NO_DATA_EXIT": {"en": "no data leaves", "fr": "aucune donnée ne sort"},
    "SWISS_HOSTING": {"en": "hosted in Switzerland", "fr": "hébergé en Suisse"},
    "OFFLINE": {"en": "works offline", "fr": "marche hors ligne"},
    "NO_THIRD_PARTY": {"en": "no tracking", "fr": "aucun suivi"},
}

# ---------------------------------------------------------------------------
# Plain-language verdict, one line per question — five languages.
# ---------------------------------------------------------------------------
PLAIN = {
    1: {
        "A": {"fr": "Le modèle d'IA tourne sur un ordinateur que l'organisation contrôle.", "de": "Das KI-Modell läuft auf einem Computer, den die Organisation selbst kontrolliert.", "it": "Il modello di IA gira su un computer controllato dall'organizzazione.", "rm": "Il model d'IA funcziuna sin in computer che l'organisaziun controllescha.", "en": "The AI model runs on a computer the organisation controls."},
        "B": {"fr": "Le modèle d'IA tourne chez un hébergeur en Suisse.", "de": "Das KI-Modell läuft bei einem Anbieter in der Schweiz.", "it": "Il modello di IA gira presso un fornitore in Svizzera.", "rm": "Il model d'IA funcziuna tar in purschider en Svizra.", "en": "The AI model runs at a hosting provider in Switzerland."},
        "C": {"fr": "On ne peut pas vérifier où tourne le modèle : cela dépend de l'installation.", "de": "Wo das Modell läuft, lässt sich nicht prüfen: Es hängt von der Installation ab.", "it": "Non si può verificare dove gira il modello: dipende dall'installazione.", "rm": "I na sa lascha betg verifitgar nua ch'il model funcziuna: quai dependa da l'installaziun.", "en": "We cannot verify where the model runs: it depends on how it is installed."},
        "D": {"fr": "Le modèle d'IA tourne chez une entreprise à l'étranger.", "de": "Das KI-Modell läuft bei einem Unternehmen im Ausland.", "it": "Il modello di IA gira presso un'azienda all'estero.", "rm": "Il model d'IA funcziuna tar ina interpresa a l'exteriur.", "en": "The AI model runs at a company abroad."},
        "E": {"fr": "Le modèle d'IA est un service fermé, à l'étranger.", "de": "Das KI-Modell ist ein geschlossener Dienst im Ausland.", "it": "Il modello di IA è un servizio chiuso, all'estero.", "rm": "Il model d'IA è in servetsch serrà a l'exteriur.", "en": "The AI model is a closed service abroad."},
        "unknown": {"fr": "Aucune trace du modèle utilisé : inconnu.", "de": "Keine Spur des verwendeten Modells: unbekannt.", "it": "Nessuna traccia del modello usato: sconosciuto.", "rm": "Nagina fastiz dal model duvrà: nunenconuschent.", "en": "No trace of which model is used: unknown."},
    },
    2: {
        "A": {"fr": "Vos questions ne quittent pas la machine.", "de": "Ihre Fragen verlassen den Rechner nicht.", "it": "Le vostre domande non lasciano il computer.", "rm": "Vossas dumondas na bandunan betg il computer.", "en": "Your questions never leave the machine."},
        "B": {"fr": "Vos données restent en Suisse.", "de": "Ihre Daten bleiben in der Schweiz.", "it": "I vostri dati restano in Svizzera.", "rm": "Vossas datas restan en Svizra.", "en": "Your data stays in Switzerland."},
        "C": {"fr": "Certaines données partent vers une destination qu'on ne sait pas situer.", "de": "Einige Daten gehen an ein Ziel, das sich nicht verorten lässt.", "it": "Alcuni dati vanno verso una destinazione che non si sa localizzare.", "rm": "Tschertas datas van ad ina destinaziun che na sa lascha betg localisar.", "en": "Some data goes to a destination we cannot locate."},
        "D": {"fr": "Des informations sur votre usage partent à l'étranger.", "de": "Informationen über Ihre Nutzung gehen ins Ausland.", "it": "Informazioni sul vostro utilizzo vanno all'estero.", "rm": "Infurmaziuns davart Voss diever van a l'exteriur.", "en": "Information about your use is sent abroad."},
        "E": {"fr": "Vos questions et vos documents quittent la Suisse.", "de": "Ihre Fragen und Dokumente verlassen die Schweiz.", "it": "Le vostre domande e i vostri documenti lasciano la Svizzera.", "rm": "Vossas dumondas e Voss documents bandunan la Svizra.", "en": "Your questions and documents leave Switzerland."},
        "unknown": {"fr": "On ne sait pas où vont les données : inconnu.", "de": "Wohin die Daten gehen, ist unbekannt.", "it": "Non si sa dove vanno i dati: sconosciuto.", "rm": "I n'è betg enconuschent nua che las datas van.", "en": "Where the data goes is unknown."},
    },
    3: {
        "A": {"fr": "Il continue de marcher sans internet, et c'est testé.", "de": "Es funktioniert auch ohne Internet, und das ist getestet.", "it": "Continua a funzionare senza internet, ed è testato.", "rm": "El funcziuna er senza internet, e quai è testà.", "en": "It keeps working without internet, and this is tested."},
        "B": {"fr": "Il devrait marcher sans internet, mais aucun test ne le prouve encore.", "de": "Es sollte ohne Internet funktionieren, aber noch beweist es kein Test.", "it": "Dovrebbe funzionare senza internet, ma nessun test lo dimostra ancora.", "rm": "El duess funcziunar senza internet, ma anc nagin test na cumprova quai.", "en": "It should work without internet, but no test proves it yet."},
        "C": {"fr": "Sans internet, le service est dégradé.", "de": "Ohne Internet ist der Dienst eingeschränkt.", "it": "Senza internet, il servizio è ridotto.", "rm": "Senza internet è il servetsch restrenschì.", "en": "Without internet, the service is degraded."},
        "D": {"fr": "Sans internet, une partie de l'outil ne se charge plus.", "de": "Ohne Internet lädt ein Teil des Werkzeugs nicht mehr.", "it": "Senza internet, una parte dello strumento non si carica più.", "rm": "Senza internet na chargia ina part da l'utensil betg pli.", "en": "Without internet, part of the tool no longer loads."},
        "E": {"fr": "Sans internet, tout s'arrête.", "de": "Ohne Internet steht alles still.", "it": "Senza internet, tutto si ferma.", "rm": "Senza internet sa ferma tut.", "en": "Without internet, everything stops."},
        "unknown": {"fr": "On ne sait pas ce qui se passe sans internet.", "de": "Was ohne Internet passiert, ist unbekannt.", "it": "Non si sa cosa succede senza internet.", "rm": "I n'è betg enconuschent tge che capita senza internet.", "en": "What happens without internet is unknown."},
    },
    4: {
        "A": {"fr": "Aucun service tiers ni suivi d'usage n'a été trouvé.", "de": "Es wurde weder ein Drittanbieter noch ein Nutzungs-Tracking gefunden.", "it": "Non è stato trovato nessun servizio terzo né tracciamento d'uso.", "rm": "I n'è vegnì chattà nagin servetsch da terzs e nagina survegliaziun dal diever.", "en": "No third-party service or usage tracking was found."},
        "B": {"fr": "Seuls des prestataires suisses sont dans la boucle.", "de": "Nur Schweizer Anbieter sind beteiligt.", "it": "Sono coinvolti solo fornitori svizzeri.", "rm": "Mo purschiders svizzers èn participads.", "en": "Only Swiss providers are in the loop."},
        "C": {"fr": "Le projet dit n'avoir aucun tiers, sans que le code permette de le vérifier.", "de": "Das Projekt gibt an, keine Drittanbieter zu nutzen, aber der Code lässt das nicht prüfen.", "it": "Il progetto dice di non avere terzi, ma il codice non permette di verificarlo.", "rm": "Il project di da na duvrar nagins terzs, ma il code na lubescha betg da verifitgar quai.", "en": "The project says it has no third parties, but the code gives nothing to check."},
        "D": {"fr": "Un composant envoie des statistiques d'usage à l'étranger par défaut.", "de": "Eine Komponente sendet standardmässig Nutzungsstatistiken ins Ausland.", "it": "Un componente invia per impostazione predefinita statistiche d'uso all'estero.", "rm": "Ina cumponenta tramet tenor standard statisticas da diever a l'exteriur.", "en": "A component sends usage statistics abroad by default."},
        "E": {"fr": "Des outils de suivi observent les utilisateurs.", "de": "Tracking-Werkzeuge beobachten die Nutzenden.", "it": "Strumenti di tracciamento osservano gli utenti.", "rm": "Utensils da survegliaziun observan las utilisadras e ils utilisaders.", "en": "Tracking tools observe the users."},
        "unknown": {"fr": "Certains composants ne peuvent pas être audités : inconnu.", "de": "Einige Komponenten lassen sich nicht prüfen: unbekannt.", "it": "Alcuni componenti non si possono verificare: sconosciuto.", "rm": "Tschertas cumponentas na sa laschan betg verifitgar: nunenconuschent.", "en": "Some components cannot be audited: unknown."},
    },
    5: {
        "A": {"fr": "Tout est public, et n'importe qui peut le revérifier.", "de": "Alles ist öffentlich und kann von allen nachgeprüft werden.", "it": "Tutto è pubblico e chiunque può ricontrollarlo.", "rm": "Tut è public e mintgin po controllar quai danovamain.", "en": "Everything is public, and anyone can re-check it."},
        "B": {"fr": "Le code est public ; on peut en revérifier la plus grande partie.", "de": "Der Code ist öffentlich; das meiste lässt sich nachprüfen.", "it": "Il codice è pubblico; gran parte si può ricontrollare.", "rm": "Il code è public; la gronda part sa lascha controllar.", "en": "The code is public; most of it can be re-checked."},
        "C": {"fr": "Le code est lisible, mais on ne peut pas le reconstruire à l'identique.", "de": "Der Code ist lesbar, lässt sich aber nicht identisch nachbauen.", "it": "Il codice è leggibile, ma non si può ricostruire in modo identico.", "rm": "Il code è legibel, ma el na sa lascha betg reconstruir identic.", "en": "The code is readable, but it cannot be rebuilt identically."},
        "D": {"fr": "Sans licence ouverte, personne ne peut réutiliser le code.", "de": "Ohne offene Lizenz darf niemand den Code wiederverwenden.", "it": "Senza licenza aperta, nessuno può riutilizzare il codice.", "rm": "Senza licenza averta na po nagin duvrar danovamain il code.", "en": "Without an open licence, nobody may reuse the code."},
        "E": {"fr": "Il n'y a rien à vérifier : aucun code publié.", "de": "Es gibt nichts zu prüfen: kein Code veröffentlicht.", "it": "Non c'è niente da verificare: nessun codice pubblicato.", "rm": "I na dat nagut da verifitgar: nagin code publitgà.", "en": "There is nothing to check: no code published."},
        "unknown": {"fr": "Vérifiabilité inconnue.", "de": "Überprüfbarkeit unbekannt.", "it": "Verificabilità sconosciuta.", "rm": "Verifitgabilitad nunenconuschenta.", "en": "Verifiability unknown."},
    },
}


def reason_text(code: str, params: dict, lang: str = "en") -> str:
    t = REASON.get(code, {}).get(lang) or REASON.get(code, {}).get("en") or code
    try:
        return t.format(**params)
    except (KeyError, IndexError):
        return t


def fix_text(code: str, lang: str = "en") -> str:
    return FIX.get(code, {}).get(lang) or FIX.get(code, {}).get("en") or code
