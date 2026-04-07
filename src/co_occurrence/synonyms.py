"""Diccionario de sinónimos de keywords y stoplist.

Archivo separado para facilitar edición manual.
Ampliar con inspección del corpus: ejecutar
`normalize.build_synonym_candidates()` para detectar candidatos.
"""

# ---------------------------------------------------------------------------
# Sinónimos: variante → forma canónica
# Criterio: la forma canónica es el nombre completo más reconocible
# en la literatura metodológica/turística.
# ---------------------------------------------------------------------------
KEYWORD_SYNONYMS: dict[str, str] = {
    # ── Structural Equation Modeling ──────────────────────────────────────
    "sem": "structural equation modeling",
    "structural equation model": "structural equation modeling",
    "structural equation modelling": "structural equation modeling",
    "structural equations": "structural equation modeling",
    "structural equations model": "structural equation modeling",
    # ── PLS-SEM ───────────────────────────────────────────────────────────
    "pls-sem": "partial least squares",
    "pls": "partial least squares",
    "partial least squares sem": "partial least squares",
    "partial least squares variant": "partial least squares",
    # ── Factor Analysis ───────────────────────────────────────────────────
    "efa": "exploratory factor analysis",
    "factor analysis": "exploratory factor analysis",
    "principle factor analysis": "exploratory factor analysis",
    "cfa": "confirmatory factor analysis",
    # ── Principal Component Analysis ──────────────────────────────────────
    "pca": "principal component analysis",
    "categorical principal components analysis": "principal component analysis",
    # ── Cluster Analysis ──────────────────────────────────────────────────
    "clustering": "cluster analysis",
    "clustering methods": "cluster analysis",
    "multivariate clustering": "cluster analysis",
    "cluster fuzzy k-means": "cluster analysis",
    "k-means": "cluster analysis",
    "hierarchical clustering": "hierarchical cluster analysis",
    "model-based cluster analysis": "cluster analysis",
    # ── Discriminant Analysis ─────────────────────────────────────────────
    "fisher discriminant analysis": "discriminant analysis",
    # ── MANOVA / ANOVA ────────────────────────────────────────────────────
    "manova": "multivariate analysis of variance",
    "anova": "analysis of variance",
    # ── Regression (general) ──────────────────────────────────────────────
    "regression": "regression analysis",
    "linear regression": "regression analysis",
    "multiple regression analysis": "multiple regression",
    "multiple linear regression": "multiple regression",
    "multivariate linear regression": "multiple regression",
    "multivariate linear regression model": "multiple regression",
    "multivariate linear regression analysis": "multiple regression",
    "multivariate regression": "multiple regression",
    "multivariate regression models": "multiple regression",
    "multivariate regression analyses": "multiple regression",
    "multivariate multiple regression": "multiple regression",
    "multivariate regression analysis": "multiple regression",
    "panel data multivariate regression analyses": "multiple regression",
    # ── Logistic Regression ───────────────────────────────────────────────
    "logistic regression": "logistic regression analysis",
    "logit": "logistic regression analysis",
    "multinominal logit model": "logistic regression analysis",
    "multinomial logistic regression": "logistic regression analysis",
    "probit": "logistic regression analysis",
    "multivariate probit analysis": "logistic regression analysis",
    # ── Quantile Regression ───────────────────────────────────────────────
    "quantile regression analysis": "quantile regression",
    # ── Correspondence Analysis ───────────────────────────────────────────
    "multi-correspondence analysis": "multiple correspondence analysis",
    "mca": "multiple correspondence analysis",
    "ca": "correspondence analysis",
    # ── Multidimensional Scaling ──────────────────────────────────────────
    "mds": "multidimensional scaling",
    "multidimensional analysis": "multidimensional scaling",
    # ── Conjoint Analysis ─────────────────────────────────────────────────
    "conjoint": "conjoint analysis",
    # ── Canonical Correlation ─────────────────────────────────────────────
    # "canonical correlation analysis" ya es canónico (1 ocurrencia)
    # ── Data Envelopment Analysis ─────────────────────────────────────────
    "dea": "data envelopment analysis",
    "data envelopment analysis (dea)": "data envelopment analysis",
    # ── Efficiency ────────────────────────────────────────────────────────
    "efficiency assessment": "efficiency",
    "labor efficiency": "efficiency",
    # ── VAR / Time Series ─────────────────────────────────────────────────
    "vector autoregressive model": "vector autoregression",
    "vector autoregression model": "vector autoregression",
    "unrestricted vector autoregressive model": "vector autoregression",
    "var": "vector autoregression",
    "vecm": "vector autoregression",
    # ── Singular Spectrum Analysis ────────────────────────────────────────
    "multivariate singular spectrum analysis": "singular spectrum analysis",
    "mssa": "singular spectrum analysis",
    "ssa": "singular spectrum analysis",
    # ── Cointegration ─────────────────────────────────────────────────────
    "cointegration test": "cointegration",
    # ── Panel Data ────────────────────────────────────────────────────────
    "panel data analysis": "panel data",
    "panel data model": "panel data",
    # ── Granger Causality ─────────────────────────────────────────────────
    "asymmetric granger causality": "granger causality",
    "symmetric and asymmetric granger causality test": "granger causality",
    "bootstrap multivariate asymmetric panel granger causality test": "granger causality",
    "panel causality": "granger causality",
    # ── Importance-Performance Analysis ───────────────────────────────────
    "ipa": "importance-performance analysis",
    "importance performance analysis": "importance-performance analysis",
    # ── AHP / ANP ─────────────────────────────────────────────────────────
    "ahp": "analytic hierarchy process",
    "anp": "analytic network process",
    "anp and improved-topsis": "analytic network process",
    # ── Neural Networks / Deep Learning ───────────────────────────────────
    "neural network": "artificial neural network",
    "ann": "artificial neural network",
    # "deep learning" se mantiene separado — no es lo mismo que ANN clásica
    "lssvm": "support vector machine",
    "two-stage hybrid sem-ann": "artificial neural network",
    # ── Fuzzy QCA ─────────────────────────────────────────────────────────
    "fsqca": "fuzzy-set qualitative comparative analysis",
    "fuzzy set": "fuzzy-set qualitative comparative analysis",
    "fuzzy set/qualitative comparative analysis (fs/qca)": "fuzzy-set qualitative comparative analysis",
    "clear-set qualitative comparative analysis (csqca)": "qualitative comparative analysis",
    "configurational analysis": "qualitative comparative analysis",
    # ── Social Network Analysis ───────────────────────────────────────────
    "sna": "social network analysis",
    "network approach": "social network analysis",
    # ── Self-Organizing Maps ──────────────────────────────────────────────
    "som": "self-organizing maps",
    # ── Mediation / Moderation ────────────────────────────────────────────
    "mediation analysis": "mediation",
    "multi-group analysis": "moderation",
    # ── Path Analysis ─────────────────────────────────────────────────────
    # "path analysis" ya es canónico (1 ocurrencia)
    # ── Wavelet ───────────────────────────────────────────────────────────
    # "wavelet analysis" ya es canónico (1 ocurrencia)
    # ── SERVQUAL ──────────────────────────────────────────────────────────
    "servqual": "service quality",
    # ── Multivariate analysis (genérico) ──────────────────────────────────
    "multivariate statistical analysis": "multivariate analysis",
    "multivariate statistics": "multivariate analysis",
    "multivariate statistical": "multivariate analysis",
    "multivariate statistical data analysis": "multivariate analysis",
    "multivariate statistical techniques": "multivariate analysis",
    "multivariate analyses": "multivariate analysis",
    "spatial multivariate analysis": "multivariate analysis",
    "quantitative methods": "multivariate analysis",
    "statistical analysis": "multivariate analysis",
    "multivariate time-series": "multivariate time series",
    "multivariate time series clustering": "multivariate time series",
    # ── Demand / Forecasting ──────────────────────────────────────────────
    "tourism demand": "tourism demand forecasting",
    "demand forecasting": "tourism demand forecasting",
    "demand": "tourism demand forecasting",
    "short term tourism demand forecast": "tourism demand forecasting",
    "interpretable tourism demand forecasting": "tourism demand forecasting",
    "tourism demands": "tourism demand forecasting",
    # ── COVID-19 ──────────────────────────────────────────────────────────
    "covid-19 pandemic": "covid-19",
    "pandemic covid-19": "covid-19",
    "after covid-19 tourism": "covid-19",
    "coronavirus": "covid-19",
    "covid-19 vaccination": "covid-19",
    "covid-19 vaccine": "covid-19",
    # ── Satisfaction ──────────────────────────────────────────────────────
    "tourist satisfaction": "satisfaction",
    "customer satisfaction": "satisfaction",
    "trip satisfaction": "satisfaction",
    "visitors' satisfaction": "satisfaction",
    # ── Motivation ────────────────────────────────────────────────────────
    "motivations": "motivation",
    "generic motivation": "motivation",
    "travelmotivation": "motivation",
    "recreation motivation": "motivation",
    "protection motivation": "motivation",
    # ── Loyalty ───────────────────────────────────────────────────────────
    "destination loyalty": "loyalty",
    "loyalty programmes": "loyalty",
    # ── Segmentation ──────────────────────────────────────────────────────
    "market segmentation": "segmentation",
    "customer segmentation": "segmentation",
    "visitor segmentation": "segmentation",
    "activity-based segmentation": "segmentation",
    "tourism segmentation": "segmentation",
    # ── Destination Image ─────────────────────────────────────────────────
    "affective image": "destination image",
    "destination brand perception": "destination image",
    "touristic image": "destination image",
    # ── Competitiveness ───────────────────────────────────────────────────
    "tourism competitiveness": "competitiveness",
    "destinations' competitiveness": "competitiveness",
    # ── Hospitality ───────────────────────────────────────────────────────
    "hospitality industry": "hospitality",
    "hotel industry": "hospitality",
    "hospitality and tourism": "hospitality",
    "hospitality and tourism management": "hospitality",
    "hospitality and tourism employees": "hospitality",
    # ── Online Reviews ────────────────────────────────────────────────────
    "user-generated reviews": "online reviews",
    # ── Consumer Behavior ─────────────────────────────────────────────────
    "consumer behaviour": "consumer behavior",
    "consuming behavior": "consumer behavior",
    # ── Ecotourism ────────────────────────────────────────────────────────
    "ecotourism development": "ecotourism",
    "ecotourismintention": "ecotourism",
    # ── Rural Tourism ─────────────────────────────────────────────────────
    "agri-tourism": "agritourism",
    "agritourism operations": "agritourism",
    # ── Gastronomy Tourism ────────────────────────────────────────────────
    "gastronomy tourism": "gastronomy",
    "gastronomic tourism": "gastronomy",
    "culinary tourism": "gastronomy",
    "food tourism": "gastronomy",
    # ── Heritage ──────────────────────────────────────────────────────────
    "world heritage site": "world heritage sites",
    "whs": "world heritage sites",
    "historical and cultural heritage": "cultural heritage",
    "unesco heritage": "cultural heritage",
    # ── Intention ─────────────────────────────────────────────────────────
    "travel intention": "behavioral intention",
    "travel intentions": "behavioral intention",
    "intention": "behavioral intention",
    "revisit intention": "behavioral intention",
    "revisit intentions": "behavioral intention",
    "travelers' intention": "behavioral intention",
    "green travel intention": "behavioral intention",
    "entrepreneurial intention": "behavioral intention",
    # ── Perception ────────────────────────────────────────────────────────
    "residents' perceptions": "perception",
    "impact perception": "perception",
    # ── Well-being / Quality of Life ──────────────────────────────────────
    "wellbeing": "well-being",
    "quality of life": "well-being",
    "quality of life (qol)": "well-being",
    "happiness": "well-being",
    # ── Theory of Planned Behavior ────────────────────────────────────────
    "theory of planned behaviour (tpb)": "theory of planned behavior",
    # ── Revenue Management ────────────────────────────────────────────────
    "revenue management": "revenue management",
    # ── Biplot (técnica de visualización) ──────────────────────────────────
    "perceptual maps": "biplot",
    # ── Carbon Emissions ──────────────────────────────────────────────────
    "co2 emissions": "carbon emissions",
    "carbon dioxide emission": "carbon emissions",
    # ── Sustainable Development ───────────────────────────────────────────
    "sustainable development goals": "sustainable development",
}


# ---------------------------------------------------------------------------
# Stoplist: keywords que se filtran del grafo de co-ocurrencia
# porque son ruido geográfico, demasiado genéricas, o no aportan
# a la estructura temático-metodológica del corpus.
# ---------------------------------------------------------------------------
KEYWORD_STOPLIST: set[str] = {
    # ── Geográficas ───────────────────────────────────────────────────────
    "ap vojvodina",
    "asia",
    "asia pacific",
    "barbados",
    "beijing-tianjin-hebei region",
    "brazil",
    "brunei bay",
    "canada",
    "cape town",
    "china",
    "china's provinces",
    "colombia",
    "cox's bazar",
    "croatia",
    "dubrovnik - neretva county",
    "eastern europe",
    "ecuador",
    "europe",
    "extremadura",
    "greece",
    "iceland",
    "india",
    "indonesia",
    "italy",
    "jordan",
    "kazakhstan",
    "korea",
    "latin america",
    "maine",
    "mediterranean",
    "mediterranean region",
    "mekong delta",
    "mexico",
    "montenegro",
    "new zealand",
    "oeiras, piaui, brazil",
    "pingyao",
    "poland",
    "poland, turkey",
    "portugal",
    "rio de janeiro",
    "south africa",
    "spain",
    "taiwan",
    "thailand",
    "the philippines",
    "thanh hoa",
    "thanh hoa province",
    "three gorges reservoir",
    "turkey",
    "turkestan",
    "uk",
    "united kingdom",
    "united states",
    "vietnam",
    "washington, dc",
    "the city of zagreb",
    "the sava river",
    "andaman sea",
    "colombian caribbean",
    "mexican caribbean contamination",
    "huangshan",
    "jiuqu stream",
    "chapada diamantina",
    "almagro",
    "bromo tengger",
    "baishatun",
    "central region",
    "territories of the russian arctic",
    # ── Genéricas que no aportan estructura ────────────────────────────────
    "study",
    "keywords",
    "factor",
    "assessment",
    "validation",
    "modeling",
    "set",
    "impact",
    "nodes",
    "space",
    "region",
    "challenges",
    "determinant factors",
    "key factors",
    "influencing factors",
    "influencing factor",
    "trends",
    "quality",
    "interest",
    "driver",
    "experiences",
    "experience",
}
