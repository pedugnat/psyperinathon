import pandas as pd
import numpy as np

def val(df, col):
    return df.loc[col][-1]


def get_revenu_moyen_femme(df):
    """return (
        val(df, "Revenu hebdomadaire moyen d'une femme")
        * val(df, "Part des femmes employées avant la naissance")
        / 100
        * val(df, "Part des femmes reprenant un emploi après la naissance")
        / 100
        * ((val(df, "Part des femmes reprenant à plein temps") / 100) + 1)
        * 0.5
    )"""

    return (
        val(df, "Revenu hebdomadaire moyen d'une femme")
        * 0.74
        * 0.75
        * 0.60
    )


def process_values(df_variables, depression=True, anxiete=True, psychose=True):

    if "nom_variable" in df_variables.columns:
        df_variables = df_variables.set_index("nom_variable")

    revenu_moyen_hebdo_femme_post_naissance = get_revenu_moyen_femme(df_variables)
    print(revenu_moyen_hebdo_femme_post_naissance)

    if depression:
        # DEPRESSION MERE
        cdmsp_sante_social = val(
            df_variables,
            "Coûts attribuables à dépréssion périnatale pour le secteur public",
        )
        cdmsoc_qaly = (
            val(df_variables, "Durée moyenne d'une dépréssion périnatale")
            * val(df_variables, "Indice de perte de qualité de vie pour la dépression")
            * val(df_variables, "Valeur d'une année de QALY")
        )

        cdmsoc_perte_prod = (
            val(df_variables, "Durée moyenne d'une dépréssion périnatale")
            * val(df_variables, "Réduction des semaines de travail chaque année")
            * revenu_moyen_hebdo_femme_post_naissance
        )

        # DEPRESSION BEBE
        # Secteur Public
        cdbsp_sante_social = (
            val(df_variables, "Coût pour la Sécu d'une naissance prématurée liée à la dépression maternelle")
            + val(df_variables, "Coût des problèmes émotionnels pour le bébé")
            + (
                val(
                    df_variables, "Probabilité supplémentaire de troubles du comportement"
                )
                / 100
            )
            * val(df_variables, "Coût pour la Sécu des troubles du comportement par cas")
        )

        cdbsp_educ = val(df_variables, "Coûts supplémentaires pour l'éducation")
        cdbsp_justice = val(df_variables, "Coût total pour la justice")

        # Société
        cdbsoc_qaly = (
            - 0
            - 0
            + val(
                df_variables,
                "Perte de qualité vie due à des troubles du comportement (en QALY)",
            )
            * val(df_variables, "Valeur d'une année de QALY")
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
            + val(
                df_variables, "Coûts supplémentaires des problèmes émotionnels (en QALY)"
            )
            + val(df_variables, "Probabilité supplémentaire de mort de l'enfant")
            / 100
            * val(df_variables, "Prix d'une vie")
            * int(1e6)
        )

        cdbsoc_perte_prod = (
            val(df_variables, "Coût en perte de productivité des problèmes émotionnels")
            + val(
                df_variables,
                "Coût en perte de productivité des troubles du comportement par cas",
            )
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
            + val(df_variables, "Coût lié à l'abandon de l'école sans qualification")
        )

        cdbsoc_autres = (
            val(df_variables, "Coût suppl total pour victimes crimes et délits par cas")
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
        )

    if anxiete:
        # ANXIETE MERE
        camsp_sante_social = val(
            df_variables, "Coût attribuable à l'anxiété périnat par femme chaque année"
        ) * val(df_variables, "Durée moyenne de l'anxiété")

        camsoc_qaly = (
            val(df_variables, "Perte de qualité de vie pour la mère en cas d'anxiété")
            * val(df_variables, "Durée moyenne de l'anxiété")
            * val(df_variables, "Valeur d'une année de QALY")
        )

        camsoc_perte_prod = (
            val(df_variables, "Nombre de semaines de travail perdues chaque année")
            * revenu_moyen_hebdo_femme_post_naissance
            * val(df_variables, "Durée moyenne de l'anxiété")
        )

        # ANXIETE BEBE
        cabsp_sante_social = (
            val(df_variables, "Coût pour le service public d'une naissance prématurée")
            * val(
                df_variables, "Risque suppl. de naissance prématurée en cas d'anxiété"
            )
            / 100
            + val(df_variables, "Coût des problèmes émotionnels en cas d'anxiété")
            + val(df_variables, "Coût pour la Sécu des troubles du comportement par cas")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
            + val(
                df_variables,
                "Coût pour le service public de douleur abdominale chronique pédiatrique par an",
            )
            * val(
                df_variables,
                "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
            )
            / 100
            * val(
                df_variables,
                "Durée moyenne des douleurs abdominales chroniques en année",
            )
        )

        cabsp_educ = val(df_variables, "Coût lié aux problèmes émotionnels si anxiété")

        cabsp_justice = (
            val(df_variables, "Coût pour la justice des troubles du comportement par cas")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
        )

        cabsoc_qaly = (
            val(df_variables, "Coût de perte de qualité de vie si anxiété (en QALY)")
            + val(df_variables, "Coûts des problème emotionnels (en QALY)")
            + val(df_variables, "Coûts des troubles du comportement par cas (en QALY)")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
        )

        cabsoc_perte_prod = (
            val(
                df_variables,
                "Coût de pertes de productivité liées aux problèmes émotionnels",
            )
            + val(
                df_variables,
                "Coût en perte de productivité des troubles du comportement par cas",
            )
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
            + val(df_variables, "Coût lié aux douleurs abdominales chroniques")
            * val(
                df_variables,
                "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
            )
            / 100
            * val(
                df_variables,
                "Durée moyenne des douleurs abdominales chroniques en année",
            )
        )

        cabsoc_autres = val(
            df_variables, "Coût suppl total pour victimes crimes et délits par cas"
        ) * val(
            df_variables, "Risque supplémentaire de troubles du comportement"
        ) / 100 + (
            val(df_variables, "Coût unpaid care douleurs abdo chroniques")
            + val(df_variables, "Coût out-of-pocket lié douleurs abdo chroniques")
        ) * val(
            df_variables,
            "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
        ) / 100 * val(
            df_variables, "Durée moyenne des douleurs abdominales chroniques en année"
        )

    if psychose:
        # PSYCHOSE MERE
        cpmsp_sante_social = val(df_variables, "Coût pour la Sécu d'une psychose")

        cpmsoc_qaly = val(
            df_variables, "Risque supplémentaire de suicide en cas de psychose"
        ) / 100 * val(df_variables, "Prix d'une vie") * int(1e6) + val(
            df_variables, "Perte de qualité de vie pour une psychose"
        ) * val(
            df_variables, "Durée moyenne d'une psychose"
        ) * val(
            df_variables, "Valeur d'une année de QALY"
        )

        cpmsoc_perte_prod = (
            val(df_variables, "Perte de productivité en cas d'épisode de schizophrènie")
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

        cpmsoc_autres = (
            val(df_variables, "Coût unpaid care en cas de schizophrénie")
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

        # PSYCHOSE BEBE
        cpbsp_sante_social = (
            val(df_variables, "Risque supplémentaire de naissance prématurée")
            / 100
            * val(
                df_variables, "Coût pour le service public d'une naissance prématurée"
            )
        )

        cpbsoc_qaly = (
            val(df_variables, "Risque supplémentaire de mort de l'enfant")
            / 100
            * val(df_variables, "Prix d'une vie")
            * int(1e6)
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

    # COUT DEPRESSION
    cout_depression_mere_SP = cdmsp_sante_social
    cout_depression_mere_SOC = cdmsoc_qaly + cdmsoc_perte_prod

    cout_depression_bebe_SP = cdbsp_sante_social + cdbsp_educ + cdbsp_justice
    cout_depression_bebe_SOC = cdbsoc_qaly + cdbsoc_perte_prod + cdbsoc_autres

    # COUT ANXIETE
    cout_anxiete_mere_SP = camsp_sante_social
    cout_anxiete_mere_SOC = camsoc_qaly + camsoc_perte_prod

    cout_anxiete_bebe_SP = cabsp_sante_social + cabsp_educ + cabsp_justice
    cout_anxiete_bebe_SOC = cabsoc_qaly + cabsoc_perte_prod + cabsoc_autres

    # COUT PSYCHOSE
    cout_psychose_mere_SP = cpmsp_sante_social
    cout_psychose_mere_SOC = cpmsoc_qaly + cpmsoc_perte_prod + cpmsoc_autres

    cout_psychose_bebe_SP = cpbsp_sante_social
    cout_psychose_bebe_SOC = cpbsoc_qaly

    # COUT PAR MALADIE
    cout_depression_mere = int(cout_depression_mere_SP + cout_depression_mere_SOC)
    cout_depression_bebe = int(cout_depression_bebe_SP + cout_depression_bebe_SOC)

    cout_anxiete_mere = int(cout_anxiete_mere_SP + cout_anxiete_mere_SOC)
    cout_anxiete_bebe = int(cout_anxiete_bebe_SP + cout_anxiete_bebe_SOC)

    cout_psychose_mere = int(cout_psychose_mere_SP + cout_psychose_mere_SOC)
    cout_psychose_bebe = int(cout_psychose_bebe_SP + cout_psychose_bebe_SOC)

    # TOTAL PAR MALADIE
    cout_depression = cout_depression_mere + cout_depression_bebe
    cout_anxiete = cout_anxiete_mere + cout_anxiete_bebe
    cout_psychose = cout_psychose_mere + cout_psychose_bebe

    couts = [
        [
            cout_depression_mere,
            cout_depression_bebe,
            cout_depression_mere + cout_depression_bebe,
        ],
        [cout_anxiete_mere, cout_anxiete_bebe, cout_anxiete_mere + cout_anxiete_bebe],
        [
            cout_psychose_mere,
            cout_psychose_bebe,
            cout_psychose_mere + cout_psychose_bebe,
        ],
    ]

    df_par_cas = pd.DataFrame(
        couts,
        columns=["Mère", "Bébé", "Total"],
        index=["Dépression périnatale", "Anxiété périnatale", "Psychose périnatale"],
    )

    # Calcul de la répartition des dépenses en fonction du secteur
    total_sante_social = sum(
        [
            cdmsp_sante_social,
            cdbsp_sante_social,
            camsp_sante_social,
            cabsp_sante_social,
            cpmsp_sante_social,
            cpbsp_sante_social,
        ]
    )
    total_autre_servicepublic = sum(
        [cdbsp_educ, cdbsp_justice, cabsp_educ, cabsp_justice]
    )
    total_societe_entiere = sum(
        [
            cout_depression_mere_SOC,
            cout_depression_bebe_SOC,
            cout_anxiete_mere_SOC,
            cout_anxiete_bebe_SOC,
            cout_psychose_mere_SOC,
            cout_psychose_bebe_SOC,
        ]
    )

    total_secteurs = (
        total_sante_social + total_autre_servicepublic + total_societe_entiere
    )

    repartition = {
        "Santé et social": int(total_sante_social) / total_secteurs,
        "Secteur public <br>(éducation, justice, etc.)": int(total_autre_servicepublic) / total_secteurs,
        "Société entière<br>(perte de chance, <br>de qualité de vie, <br>de productivité, etc.)": int(total_societe_entiere) / total_secteurs,
    }

    df_repartition_secteur = pd.DataFrame(repartition, index=["Répartition des coûts par secteur"]).T

    return df_par_cas, df_repartition_secteur








def process_values_sensi(df_variables, depression=True, anxiete=True, psychose=True):

    if "nom_variable" in df_variables.columns:
        df_variables = df_variables.set_index("nom_variable")

    revenu_moyen_hebdo_femme_post_naissance = get_revenu_moyen_femme(df_variables)

    if depression:
        # DEPRESSION MERE
        cdmsp_sante_social = val(
            df_variables,
            "Coûts attribuables à dépréssion périnatale pour le secteur public",
        )
        cdmsoc_qaly = (
            val(df_variables, "Durée moyenne d'une dépréssion périnatale")
            * val(df_variables, "Indice de perte de qualité de vie pour la dépression")
            * val(df_variables, "Valeur d'une année de QALY")
        )

        cdmsoc_perte_prod = (
            val(df_variables, "Durée moyenne d'une dépréssion périnatale")
            * val(df_variables, "Réduction des semaines de travail chaque année")
            * revenu_moyen_hebdo_femme_post_naissance
        )

        # DEPRESSION BEBE
        # Secteur Public
        cdbsp_sante_social = (
            val(df_variables, "Coût pour la Sécu d'une naissance prématurée liée à la dépression maternelle")
            + val(df_variables, "Coût des problèmes émotionnels pour le bébé")
            + (
                val(
                    df_variables, "Probabilité supplémentaire de troubles du comportement"
                )
                / 100
            )
            * val(df_variables, "Coût pour la Sécu des troubles du comportement par cas")
        )

        cdbsp_educ = val(df_variables, "Coûts supplémentaires pour l'éducation")
        cdbsp_justice = val(df_variables, "Coût total pour la justice")

        # Société
        cdbsoc_qaly = (
            - 0
            - 0
            + val(
                df_variables,
                "Perte de qualité vie due à des troubles du comportement (en QALY)",
            )
            * val(df_variables, "Valeur d'une année de QALY")
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
            + val(
                df_variables, "Coûts supplémentaires des problèmes émotionnels (en QALY)"
            )
            + val(df_variables, "Probabilité supplémentaire de mort de l'enfant")
            / 100
            * val(df_variables, "Prix d'une vie")
            * int(1e6)
        )

        cdbsoc_perte_prod = (
            val(df_variables, "Coût en perte de productivité des problèmes émotionnels")
            + val(
                df_variables,
                "Coût en perte de productivité des troubles du comportement par cas",
            )
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
            + val(df_variables, "Coût lié à l'abandon de l'école sans qualification")
        )

        cdbsoc_autres = (
            val(df_variables, "Coût suppl total pour victimes crimes et délits par cas")
            * val(df_variables, "Probabilité supplémentaire de troubles du comportement")
            / 100
        )

    if anxiete:
        # ANXIETE MERE
        camsp_sante_social = val(
            df_variables, "Coût attribuable à l'anxiété périnat par femme chaque année"
        ) * val(df_variables, "Durée moyenne de l'anxiété")

        camsoc_qaly = (
            val(df_variables, "Perte de qualité de vie pour la mère en cas d'anxiété")
            * val(df_variables, "Durée moyenne de l'anxiété")
            * val(df_variables, "Valeur d'une année de QALY")
        )

        camsoc_perte_prod = (
            val(df_variables, "Nombre de semaines de travail perdues chaque année")
            * revenu_moyen_hebdo_femme_post_naissance
            * val(df_variables, "Durée moyenne de l'anxiété")
        )

        # ANXIETE BEBE
        cabsp_sante_social = (
            val(df_variables, "Coût pour le service public d'une naissance prématurée")
            * val(
                df_variables, "Risque suppl. de naissance prématurée en cas d'anxiété"
            )
            / 100
            + val(df_variables, "Coût des problèmes émotionnels en cas d'anxiété")
            + val(df_variables, "Coût pour la Sécu des troubles du comportement par cas")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
            + val(
                df_variables,
                "Coût pour le service public de douleur abdominale chronique pédiatrique par an",
            )
            * val(
                df_variables,
                "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
            )
            / 100
            * val(
                df_variables,
                "Durée moyenne des douleurs abdominales chroniques en année",
            )
        )

        cabsp_educ = val(df_variables, "Coût lié aux problèmes émotionnels si anxiété")

        cabsp_justice = (
            val(df_variables, "Coût pour la justice des troubles du comportement par cas")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
        )

        cabsoc_qaly = (
            val(df_variables, "Coût de perte de qualité de vie si anxiété (en QALY)")
            + val(df_variables, "Coûts des problème emotionnels (en QALY)")
            + val(df_variables, "Coûts des troubles du comportement par cas (en QALY)")
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
        )

        cabsoc_perte_prod = (
            val(
                df_variables,
                "Coût de pertes de productivité liées aux problèmes émotionnels",
            )
            + val(
                df_variables,
                "Coût en perte de productivité des troubles du comportement par cas",
            )
            * val(df_variables, "Risque supplémentaire de troubles du comportement")
            / 100
            + val(df_variables, "Coût lié aux douleurs abdominales chroniques")
            * val(
                df_variables,
                "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
            )
            / 100
            * val(
                df_variables,
                "Durée moyenne des douleurs abdominales chroniques en année",
            )
        )

        cabsoc_autres = val(
            df_variables, "Coût suppl total pour victimes crimes et délits par cas"
        ) * val(
            df_variables, "Risque supplémentaire de troubles du comportement"
        ) / 100 + (
            val(df_variables, "Coût unpaid care douleurs abdo chroniques")
            + val(df_variables, "Coût out-of-pocket lié douleurs abdo chroniques")
        ) * val(
            df_variables,
            "Risque suppl. d'avoir des douleurs abdominales chroniques si anxiété",
        ) / 100 * val(
            df_variables, "Durée moyenne des douleurs abdominales chroniques en année"
        )

    if psychose:
        # PSYCHOSE MERE
        cpmsp_sante_social = val(df_variables, "Coût pour la Sécu d'une psychose")

        cpmsoc_qaly = val(
            df_variables, "Risque supplémentaire de suicide en cas de psychose"
        ) / 100 * val(df_variables, "Prix d'une vie") * int(1e6) + val(
            df_variables, "Perte de qualité de vie pour une psychose"
        ) * val(
            df_variables, "Durée moyenne d'une psychose"
        ) * val(
            df_variables, "Valeur d'une année de QALY"
        )

        cpmsoc_perte_prod = (
            val(df_variables, "Perte de productivité en cas d'épisode de schizophrènie")
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

        cpmsoc_autres = (
            val(df_variables, "Coût unpaid care en cas de schizophrénie")
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

        # PSYCHOSE BEBE
        cpbsp_sante_social = (
            val(df_variables, "Risque supplémentaire de naissance prématurée")
            / 100
            * val(
                df_variables, "Coût pour le service public d'une naissance prématurée"
            )
        )

        cpbsoc_qaly = (
            val(df_variables, "Risque supplémentaire de mort de l'enfant")
            / 100
            * val(df_variables, "Prix d'une vie")
            * int(1e6)
            * val(df_variables, "Pourcentage de schizophrènes parmi psychose")
            / 100
        )

    # COUT DEPRESSION
    cout_depression_mere_SP = cdmsp_sante_social
    cout_depression_mere_SOC = cdmsoc_qaly + cdmsoc_perte_prod

    cout_depression_bebe_SP = cdbsp_sante_social + cdbsp_educ + cdbsp_justice
    cout_depression_bebe_SOC = cdbsoc_qaly + cdbsoc_perte_prod + cdbsoc_autres

    # COUT ANXIETE
    cout_anxiete_mere_SP = camsp_sante_social
    cout_anxiete_mere_SOC = camsoc_qaly + camsoc_perte_prod

    cout_anxiete_bebe_SP = cabsp_sante_social + cabsp_educ + cabsp_justice
    cout_anxiete_bebe_SOC = cabsoc_qaly + cabsoc_perte_prod + cabsoc_autres

    # COUT PSYCHOSE
    cout_psychose_mere_SP = cpmsp_sante_social
    cout_psychose_mere_SOC = cpmsoc_qaly + cpmsoc_perte_prod + cpmsoc_autres

    cout_psychose_bebe_SP = cpbsp_sante_social
    cout_psychose_bebe_SOC = cpbsoc_qaly

    # COUT PAR MALADIE
    cout_depression_mere = int(cout_depression_mere_SP + cout_depression_mere_SOC)
    cout_depression_bebe = int(cout_depression_bebe_SP + cout_depression_bebe_SOC)

    cout_anxiete_mere = int(cout_anxiete_mere_SP + cout_anxiete_mere_SOC)
    cout_anxiete_bebe = int(cout_anxiete_bebe_SP + cout_anxiete_bebe_SOC)

    cout_psychose_mere = int(cout_psychose_mere_SP + cout_psychose_mere_SOC)
    cout_psychose_bebe = int(cout_psychose_bebe_SP + cout_psychose_bebe_SOC)

    # TOTAL PAR MALADIE
    cout_depression = cout_depression_mere + cout_depression_bebe
    cout_anxiete = cout_anxiete_mere + cout_anxiete_bebe
    cout_psychose = cout_psychose_mere + cout_psychose_bebe

    couts = [
        [
            cout_depression_mere,
            cout_depression_bebe,
            cout_depression_mere + cout_depression_bebe,
        ],
        [cout_anxiete_mere, cout_anxiete_bebe, cout_anxiete_mere + cout_anxiete_bebe],
        [
            cout_psychose_mere,
            cout_psychose_bebe,
            cout_psychose_mere + cout_psychose_bebe,
        ],
    ]

    df_par_cas = pd.DataFrame(
        couts,
        columns=["Mère", "Bébé", "Total"],
        index=["Dépression périnatale", "Anxiété périnatale", "Psychose périnatale"],
    )
    
    prevalences = (
        df_variables
        .loc[
            [
                "Prévalence de " + mal
                for mal in ["la dépression", "l'anxiété", "la psychose"]
            ]
        ]
        .iloc[:, -1]
        .values
        / 100
    )

    df_par_naissance = df_par_cas.copy()
    #print(df_par_naissance.iloc[:, 1:])
    df_par_naissance.iloc[:, :] = df_par_naissance.iloc[:, :].mul(prevalences, axis=0)
    

    return df_par_naissance['Total'].sum()

