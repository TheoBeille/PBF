# PBF
Construction d'une carte pour utilisateurs de vélos Parisiens qui indique ou aller pour un meilleur itinéraire plus safe.



1. Collecte des données
    * Accidents : Données publiques des accidents impliquant des cyclistes 
    * Vols de vélos : Données de police (optionnels a faire dans un autre temps) 
    * Infrastructures : Cartographie des pistes cyclables, état des routes, feux tricolores
    * Météo/Traffic : Données historiques de trafic et de météo pour croiser avec les accidents.
  
      
2. Prétraitement et analyse exploratoire
    * Nettoyage, géolocalisation, agrégation par quartier ou tronçon de route.
    * Visualisation des zones à risque sur une carte (avec des outils comme Folium ou Plotly).
  
3. Modélisation
    * Classification : Prédire si une zone est à risque ou non.
    * Clustering : Identifier des profils de zones à risque (ex : zones avec beaucoup de vols mais peu d’accidents).

Données: 

https://opendata.paris.fr/explore/?refine.theme=Mobilité+et+Espace+Public&disjunctive.theme&disjunctive.publisher&disjunctive.keyword&disjunctive.modified&disjunctive.features&sort=modified

Il faut: 
-Les accidents qui ont eu lieu: https://opendata.paris.fr/explore/dataset/accidentologie0/export/?disjunctive.victime_type&disjunctive.gravite&disjunctive.tranche_age_victime&disjunctive.com_arm_code
-le type d'infrastructure : https://opendata.paris.fr/explore/dataset/plan-de-voirie-pistes-cyclables-et-couloirs-de-bus/information/?disjunctive.lib_classe&disjunctive.num_pave

https://opendata.paris.fr/explore/dataset/amenagements-cyclables/information/disjunctive.arrondissement&disjunctive.position_amenagement&disjunctive.vitesse_maximale_autorisee&disjunctive.source&disjunctive.amenagement BIEN PARCE QUE DECRIS LE TYPE DE PISTES

-Les travaux de chaussées en cours : https://opendata.paris.fr/explore/dataset/circulation_evenement/information/  OU https://opendata.paris.fr/explore/dataset/chantiers-perturbants/information/?disjunctive.cp_arrondissement&disjunctive.maitre_ouvrage&disjunctive.objet&disjunctive.impact_circulation&disjunctive.niveau_perturbation&disjunctive.statut

https://opendata.paris.fr/explore/dataset/secteurs-paris-respire/information/?disjunctive.nom&disjunctive.arrdt&disjunctive.jours&disjunctive.horaires_annee&disjunctive.periode_estivale&disjunctive.horaires_ete&disjunctive.autorises&disjunctive.type_secteurs

https://opendata.paris.fr/explore/dataset/historique-chantiers-a-paris-en-2024/information/

-Verbalisation: 
https://opendata.paris.fr/explore/dataset/dpmp-verbalisations/information/


Si utile possible de trouver l'historique des chantiers,
