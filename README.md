# Stickman 3D Blender · Glitch Lab

Un kit gratuit pour Claude Code : tu donnes une idée, Claude construit un short vertical de 60 à 75 secondes avec des personnages 3D (tête boule blanche au visage peint, manteau cloche, bras bâtons noirs, moufles) dans une petite ville peinte, une histoire vraie ou plausible avec un retournement, et des sous-titres d'un ou deux mots.

Tout est fabriqué dans **Blender** sur ton propre PC : personnages, expressions, poses, caméra, décors, encrage, étalonnage, sous-titres et mix du son. Pas de générateur vidéo IA.

Gratuit, sans inscription.

## Installation (une minute)
1. Ouvre **Claude Code**.
2. Colle ce message et envoie :

   > Installe-moi ce repo : https://github.com/Prisma972/glitch-lab-stickman-3d-blender

3. C'est tout. Ensuite, demande-lui : *« Fais-moi un short stickman 3D sur … »*.

Au premier short, Claude vérifie ton installation (Blender, Python, ffmpeg), copie le kit dans ton dossier de travail, construit la scène d'exemple et rend une image de contrôle avant de commencer.

**Autre méthode, avec les plugins Claude Code :**
```
/plugin marketplace add Prisma972/glitch-lab-stickman-3d-blender
/plugin install stickman-3d-blender@glitch-lab
```

## Ce qu'il te faut
- Claude Code
- Blender 5.2 ou plus récent ([blender.org](https://www.blender.org))
- Python 3.10 ou plus, avec numpy, Pillow, opencv-python et OpenEXR (Claude te demande avant d'installer quoi que ce soit)
- ffmpeg
- faster-whisper pour caler les sous-titres sur la voix
- Un PC récent (une carte graphique accélère beaucoup les rendus : compte 30 à 45 minutes pour 60 secondes)
- Ta voix off : enregistrée ou générée, en `voice.wav`

## Ce qu'il y a dedans
| Dossier | Contenu |
|---|---|
| `skills/stickman-3d-blender/SKILL.md` | La méthode complète que Claude suit : installation, histoire, script, voix, plans, construction, images de contrôle, aperçu, son, rendu |
| `skills/stickman-3d-blender/references/` | La bible du style (mesurée image par image), la procédure pas à pas, la référence du code, les leçons apprises |
| `skills/stickman-3d-blender/kit/pp/` | Le kit Blender : personnages, visages, poses et actions, marche, grammaire caméra, décors (rue, atelier, village), encrage, flou de mouvement, étalonnage, sous-titres, mix, rendu complet |
| `skills/stickman-3d-blender/kit/tex/` | Les textures : planche des expressions, enseignes, accessoires de l'atelier |
| `skills/stickman-3d-blender/kit/shorts/allumeur/` | La scène d'exemple : 8 secondes au crépuscule, un allumeur de réverbères allume une lanterne avec sa perche pendant que sa voisine lui fait signe depuis le salon de thé. C'est la preuve que tout marche chez toi |

Pour voir l'exemple tout seul : `blender -b -P shorts/allumeur/scene.py` depuis le dossier `kit/`, puis `python pp/short.py shorts/allumeur/short.json --preview`.

---

## Pour Claude : comment installer ce repo
Quand l'utilisateur te demande d'installer ce repo :
1. Clone-le dans un dossier temporaire : `git clone --depth 1 https://github.com/Prisma972/glitch-lab-stickman-3d-blender`.
2. Copie `skills/stickman-3d-blender/` (avec son dossier `kit/`) dans le dossier des skills de l'utilisateur : `~/.claude/skills/stickman-3d-blender/` (sous Windows : `%USERPROFILE%\.claude\skills\stickman-3d-blender\`). Si ce dossier existe déjà, demande avant de le remplacer.
3. Vérifie que `~/.claude/skills/stickman-3d-blender/SKILL.md` et `~/.claude/skills/stickman-3d-blender/kit/pp/short.py` existent, puis supprime le clone temporaire.
4. Dis à l'utilisateur, dans sa langue, que c'est installé. Le skill sera visible dans une nouvelle session : il pourra alors demander « fais-moi un short stickman 3D sur … ». Au premier short, suis l'étape 0 de `SKILL.md`.

## Licence
Code et documentation sous licence MIT (voir `LICENSE`). Le kit garde des leçons du skill MIT [make-short](https://github.com/nocodehack/make-short) de NoCodeHack, pas son code. Les personnages, décors, textures et la scène d'exemple sont originaux.
