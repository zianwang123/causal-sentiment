# Global Macro Impact Factor Framework

**Causal Sentiment — Factor Selection Report**
*Global Macro Research Desk*
*March 2026*

---

## Executive Summary

This report documents the 110 macro impact factors selected for our causal factor graph — the analytical backbone of our macro surveillance system. These are not investment style factors (value, momentum, carry). These are the **structural forces that move global financial markets**: the rates decisions, the credit impulses, the geopolitical shocks, the plumbing failures, the housing cycles, and the contagion chains that, when they break, produce the events that define decades.

We designed this framework with a single test: **can we trace every major market dislocation of the last 20 years through these factors?** The 2008 financial crisis. The European sovereign debt crisis. COVID. SVB. The AI boom. The yen carry unwind. If the answer is no — if a crisis happened and our graph has no path to explain it — then we have a blind spot that will cost us when the next variant of that crisis arrives.

The result is 110 factors across 17 categories, connected by approximately 200+ directed causal edges. Each factor earned its place by satisfying at least one of three criteria:

1. **It moved markets materially in a historical episode** (e.g., mortgage rates in 2008, repo rates in 2019, China credit impulse in 2015)
2. **It is a critical transmission mechanism** between factors that moved markets (e.g., bank lending standards transmit financial stress into real economy contraction)
3. **It represents a structural risk that is building but has not yet detonated** (e.g., commercial real estate stress, US fiscal sustainability, private credit opacity)

What follows is not a list. It is an argument — for each factor, why it must be on the board.

---

## Methodology

### How We Got Here

We began with the question every macro allocator must answer: **what are the state variables of the global financial system?** Not every economic indicator. Not every market price. The *minimum set* of factors such that any market-moving event can be decomposed into movements across these factors.

Our process:

1. **Historical event decomposition.** We took 12 major market dislocations (2008 GFC through 2025 tariff escalation) and reverse-engineered the causal chains. For each event, we asked: what moved first, what transmitted, what amplified, and what broke? Any factor that appeared as a critical node in 3+ events earned automatic inclusion.

2. **Transmission mechanism audit.** We mapped how monetary policy reaches the real economy, how geopolitical shocks reach asset prices, how financial stress propagates across borders. Any factor that serves as a *necessary intermediary* in these chains — even if it rarely makes headlines itself — was included. Repo rates don't trend on Bloomberg Terminal news feeds, but when they break, everything breaks.

3. **Blind spot stress test.** We asked: if we had this graph in 2007, would we have seen the housing crisis coming? If we had it in 2022, would we have caught SVB exposure? Where the answer was "no," we added factors until it became "yes."

4. **Implementability filter.** Every factor must be monitorable. Either it has a quantitative data source (FRED, yfinance, options data) or it can be systematically tracked through news/RSS analysis with clear keywords. We excluded factors that require proprietary data we cannot access (e.g., dealer inventory positions, prime brokerage leverage reports).

### What We Excluded and Why

- **Investment style factors** (value, momentum, quality, size, carry) — these describe *how* to invest, not *what moves markets*. They belong in a portfolio construction framework, not a macro surveillance system.
- **Individual company fundamentals** — Apple's iPhone sales, NVIDIA's data center revenue. These matter, but they are downstream of the macro factors we do track (tech sector, semiconductor supply, AI capex). Company-level monitoring is a different system.
- **Proprietary/inaccessible data** — dealer positioning, dark pool flows, prime brokerage leverage. Critical information, but we cannot systematically monitor it with open-source data. We proxy it where possible (e.g., CFTC COT data for institutional positioning).
- **Extremely slow-moving structural trends** — demographics, urbanization, de-globalization. These are important over decades but do not create the regime shifts and dislocations this system is designed to detect. They inform our secular views, not our causal graph.

---

## The Factor Taxonomy

### Category 1: US Macroeconomic Fundamentals (14 Factors)

**Why this category exists:** The United States is 26% of global GDP, home to the world's reserve currency, and the issuer of the global risk-free asset. Every global portfolio has direct or indirect US exposure. US macro data releases move global markets in real-time. You cannot run a macro surveillance system without granular visibility into the US economic cycle.

#### The Factors

**1. Federal Funds Rate**
The price of money. Every asset in the world is priced relative to this rate, directly or indirectly. When the Fed moved from 0% to 5.25% in 2022-23, it repriced $400 trillion in global financial assets. Mortgages, corporate bonds, equity valuations, EM debt service costs, currency carry trades — all flow from this single number. We don't just monitor the level; we monitor the *velocity* of change, because markets can absorb 500bp of tightening over 3 years but not over 18 months.

**2. US CPI Year-over-Year**
Headline inflation drives the Fed reaction function, which drives the Fed Funds Rate, which drives everything else. But CPI is also a political variable — it determines whether the sitting president wins re-election, whether Congress passes fiscal stimulus or austerity, whether the Fed chair keeps their job. The 9.1% print in June 2022 was the single data point that forced the most aggressive tightening cycle since Volcker. We decompose this into goods vs. services vs. shelter because they have different drivers and different policy implications.

**3. US GDP Growth**
The broadest measure of economic output. Matters less for its level than for its *direction* and *surprises* — when GDP comes in well below consensus, recession fears spike and risk assets sell off. The Q1 2020 collapse (-31.4% annualized) and the Q3 2020 recovery (+33.4%) were the most extreme GDP swings ever recorded. We track this quarterly but use higher-frequency proxies (PMI, jobless claims) for real-time interpolation.

**4. Unemployment Rate**
Half of the Fed's dual mandate. But the unemployment rate is a *lagging* indicator — by the time it spikes, the recession is already here. We include it because it drives Fed forward guidance ("we won't cut until unemployment rises to X"), consumer confidence, and political pressure on policy. The key is the *rate of change*: unemployment rising from 3.4% to 4.3% in 2024 triggered the "Sahm Rule" recession indicator and caused the August 5th market crash.

**5. US Manufacturing PMI (ISM)**
The oldest and most-watched leading indicator of economic activity. A reading below 50 signals contraction. Manufacturing is only ~11% of US GDP, but it is the most cyclical component and the most exposed to global trade, inventory cycles, and capex decisions. PMI has led every US recession since 1960. We include it specifically because it is *leading* where GDP is lagging.

**6. PCE Deflator**
The Fed's *stated* preferred inflation measure, distinct from CPI. The divergence between CPI and PCE matters — PCE uses different weights (lower shelter weight) and includes items CPI misses (employer-provided healthcare). When the Fed says "we're targeting 2% inflation," they mean PCE, not CPI. Watching CPI alone would give you a systematically biased read on Fed reaction.

**7. Consumer Confidence (Michigan/Conference Board)**
A soft indicator, but one that matters for two reasons. First, consumer spending is 70% of US GDP — if consumers believe the economy is deteriorating, they pull back spending, creating the recession they feared. Self-fulfilling prophecy. Second, consumer confidence collapses *precede* actual spending declines by 1-3 months, making it a useful leading indicator. The March 2020 confidence crash was one of the fastest on record.

**8. Wage Growth (Average Hourly Earnings)**
The input that determines whether inflation is transitory or persistent. Goods inflation can spike and reverse (supply chains normalize). Services inflation is sticky because it is driven by labor costs. When wages are growing at 5%+ YoY (as in 2022), the Fed cannot declare victory on inflation regardless of what goods prices are doing. Wage growth also determines real income and therefore consumer spending power. This is where the labor market meets the inflation fight.

**9. Initial Jobless Claims** *(NEW)*
We include this because it is the **highest-frequency labor market indicator available** — weekly, not monthly. It is the first domino to fall when the labor market turns. Initial claims bottomed at 166K in March 2022, then the question for 18 months was "when do they spike?" Every single US recession since 1967 was preceded by a sustained rise in initial claims. When claims crossed 250K in mid-2024, it was the first hard evidence that the labor market was softening. Monthly payrolls can be revised, unemployment rate can be distorted by participation changes — but people filing for unemployment is an unambiguous, real-time signal.

**10. JOLTS Job Openings** *(NEW)*
We include this because the Fed explicitly used the **Beveridge Curve** (job openings vs. unemployment) as their key analytical framework in 2022-23. Chair Powell repeatedly cited JOLTS data to argue that the labor market could cool through reduced openings rather than higher unemployment — the "soft landing" thesis depended on this relationship. Openings peaked at 12 million in March 2022 and the decline to 8 million by late 2023 *without* a corresponding unemployment spike was the empirical evidence that soft landing was possible. If you weren't monitoring this, you missed the analytical framework the most important central bank in the world was using to make decisions.

**11. Labor Force Participation Rate** *(NEW)*
We include this because it explains **why the unemployment rate lies.** Unemployment can be 3.5% and the labor market can still be extremely tight — if 2 million people left the workforce and aren't coming back. That is exactly what happened post-COVID: participation dropped from 63.3% to 60.1% and took 3 years to partially recover. The "missing workers" drove wage inflation because employers were bidding for a smaller labor pool. Without monitoring participation, you would have looked at a 3.5% unemployment rate and concluded the labor market was similar to 2019 — but the supply side was fundamentally different.

**12. US Services PMI** *(NEW)*
We include this because **manufacturing PMI alone gives you a distorted picture of the US economy.** Services are 70%+ of GDP. In 2022-23, manufacturing PMI was in contraction territory for months while services remained expansionary — the economy was *not* in recession despite what manufacturing data suggested. Services inflation (restaurants, healthcare, insurance, shelter) was the "last mile" problem that kept the Fed from cutting. A system that monitors manufacturing PMI but not services PMI would have incorrectly called a recession in 2023.

**13. US Fiscal Deficit** *(NEW)*
We include this because the 2023-2024 period demonstrated that **fiscal policy can override monetary policy.** The Fed was tightening at the fastest pace in 40 years, yet the economy refused to slow. Why? Because the US government was running a 6%+ GDP deficit — injecting stimulus faster than the Fed was withdrawing it. The "fiscal dominance" narrative drove the 10Y yield from 3.8% to 5.0% in late 2023, the largest bond selloff in a generation, because the market realized that (a) deficits mean more Treasury supply and (b) more supply means higher term premium. A macro system without fiscal deficit monitoring is blind to the single largest force in the current rate regime.

**14. US Productivity Growth** *(NEW)*
We include this because it determines the **speed limit of non-inflationary growth**, and the AI productivity question is the most consequential structural debate in macro today. If AI genuinely raises productivity growth from 1.5% to 3.0%, the economy can grow faster without inflation, profit margins expand, and equity valuations are justified. If it doesn't, current growth rates are inflationary and current valuations are a bubble. Productivity growth determines which of these worlds we're in. It's also the key input to potential GDP, which the Fed uses to calibrate the neutral rate.

---

### Category 2: Monetary Policy (7 Factors)

**Why this category exists:** Central banks are the most powerful actors in financial markets. A single sentence from a Fed chair can move trillions of dollars. But monetary policy is not monolithic — the Fed, ECB, BOJ, and PBOC often diverge, and the *differential* between their policies drives currency markets, capital flows, and relative asset performance. We need granular visibility into the major central banks' actions, their balance sheets, and the market's expectations for their future actions.

**15. Fed Balance Sheet**
The stock of assets the Fed holds. QE (buying) injects reserves and suppresses yields. QT (selling) drains reserves and allows yields to rise. The balance sheet expanded from $4T to $9T during COVID, then shrank to ~$7.5T through QT. The *level* matters for reserve adequacy (see: 2019 repo crisis), and the *direction* matters for liquidity conditions. We track this separately from the fed funds rate because the Fed can tighten via rate hikes AND QT simultaneously — a "double tightening" that is more restrictive than either alone.

**16. Rate Expectations (Fed Funds Futures)**
Markets move on *expectations*, not actuals. A 25bp rate hike that was 100% priced in moves nothing. A hike that was 50% priced in moves everything. The gap between current rates and the futures-implied path tells us how much tightening or easing is already in the price. In December 2023, futures priced 6-7 cuts in 2024; by April 2024, that had collapsed to 1-2 cuts. That repricing — not any actual rate change — drove the Q1 2024 bond selloff.

**17. QE/QT Pace**
Distinct from the balance sheet *level*. The Fed can hold $7T in assets but the *flow* of purchases or sales matters independently. When QE was running at $120B/month in 2021, it was directly suppressing the 10Y yield by an estimated 50-75bp. When QT accelerated to $95B/month, it was adding selling pressure to a market that was simultaneously absorbing record Treasury issuance. Flow effects compound with supply effects.

**18. Global Central Bank Liquidity**
The aggregate balance sheet of the Fed + ECB + BOJ + PBOC. This is the "global liquidity tide." When all four are expanding (2020-21), risk assets have a tailwind regardless of fundamentals. When all four are contracting (late 2022), even good news can't lift markets. The divergence matters too: when the Fed is tightening but the BOJ and PBOC are easing, it creates cross-border capital flows that drive currencies and carry trades.

**19. ECB Policy Rate** *(NEW)*
We include this because the ECB is the **second most important central bank in the world** and its policy frequently diverges from the Fed. The 2011-12 European sovereign debt crisis was *caused* by ECB policy (Trichet hiked rates into a recession). The 2022-23 inflation fight saw ECB and Fed hiking in tandem for the first time — but the ECB started later and will likely cut on a different schedule. The rate differential between ECB and Fed is the primary driver of EUR/USD, which at $7.5T daily volume is the world's most traded asset. Our system previously had no visibility into ECB actions — meaning we couldn't explain EUR/USD moves or European periphery stress.

**20. PBOC Policy** *(NEW)*
We include this because **China's monetary policy drives the world's second-largest economy and the largest marginal consumer of commodities.** When the PBOC eases (cuts RRR, injects liquidity, lowers LPR), China credit impulse rises, property developers get a reprieve, and commodity demand recovers — this cascades through iron ore, copper, AUD, and EM equities. When the PBOC tightens or fails to ease adequately (as in 2022-23 during the property crisis), the deflationary impulse hits global growth expectations. Our system had a China PMI node but no visibility into *why* China's economy was accelerating or decelerating. PBOC policy is the lever.

**21. Term Premium** *(NEW)*
We include this because the **2023 bond selloff taught the market that term premium is not dead.** For a decade after the GFC, term premium was negative (investors were *paying* for the privilege of holding long-duration Treasuries, because of QE scarcity). In 2023, term premium flipped positive and added an estimated 50-100bp to the 10Y yield. Why? Fiscal deficits, rising Treasury supply, uncertainty about long-run inflation, and foreign buyers (China, Japan) reducing purchases. Term premium is distinct from rate expectations — it measures the *compensation for uncertainty* about holding long-duration bonds. Without it, you can't decompose why the 10Y yield is moving: is it because the market expects higher rates (rate expectations) or because investors are demanding more compensation for risk (term premium)?

---

### Category 3: Geopolitics (6 Factors)

**Why this category exists:** Geopolitical events are the shocks that models don't predict. They are exogenous to economic fundamentals but endogenous to asset prices. Russia invading Ukraine was not in any economic model, but it repriced energy, food, European growth, and defense budgets for years. Our system needs to capture geopolitical risk not to *predict* wars, but to *detect and propagate* their financial consequences when they happen.

**22. Geopolitical Risk Index**
A composite measure derived from news coverage of wars, terrorism, nuclear threats, and military escalation. We include it as the broad "threat level" that affects risk premia across all assets. Spikes in GPR correlate with VIX spikes, gold rallies, and Treasury demand (flight to safety). It's the first-order read on "is the world getting more dangerous?"

**23. Trade Policy / Tariffs**
We separate trade policy from broader geopolitics because **tariff wars have distinct, traceable economic transmission mechanisms.** A 25% tariff on Chinese goods doesn't just create headline risk — it raises input costs for US manufacturers, disrupts supply chains, invites retaliation, depresses EM export economies, and creates inflation pressure. The 2018-19 tariff war took 15% off Chinese equities and inverted the yield curve. The 2025 tariff escalation is even broader in scope. This factor tracks the *regime* — the direction and magnitude of global trade barriers.

**24. US Political Risk**
Elections, policy shifts, government shutdowns, debt ceiling standoffs, and regulatory pivots. We isolate US political risk because **US policy uncertainty affects the entire world.** A US government shutdown threatens Treasury payments. A debt ceiling crisis (2011, 2023) triggers rating agency downgrades. The 2024-25 policy regime shift (tariffs, deregulation, fiscal expansion) is reshaping global trade and capital flows. This is distinct from geopolitical risk (which is about interstate conflict) — this is about domestic policy uncertainty affecting global markets.

**25. Sanctions Pressure**
We track sanctions as a distinct factor because **sanctions are now a primary tool of economic warfare** and they reshape trade flows, energy markets, and FX dynamics. Russia sanctions post-2022 rerouted global energy trade (Russian oil to India/China instead of Europe, LNG from US to Europe instead of Asia). Iran sanctions affect oil supply. China entity-list additions affect semiconductor supply chains. Sanctions don't just create binary risk (on/off) — they create persistent structural shifts in how goods, capital, and energy flow globally.

**26. Climate / Energy Transition Policy** *(NEW)*
We include this because the **energy transition is now a macro force, not just an ESG consideration.** The EU Carbon Border Adjustment Mechanism (CBAM) directly taxes imports based on carbon content — this is a trade policy as much as a climate policy. The US Inflation Reduction Act allocated $370B to clean energy — the largest industrial policy in US history. Carbon prices in the EU exceed €80/ton, directly affecting power costs, industrial competitiveness, and corporate margins. When Texas freezes (2021) or European heat waves reduce nuclear/hydro capacity, it creates energy price spikes that feed into inflation. We cannot model energy markets or industrial policy without tracking the regulatory regime around carbon.

**27. Tech / AI Regulation** *(NEW)*
We include this because **technology regulation now directly affects the largest sector of global equity markets.** US chip export controls to China (October 2022, October 2023, January 2025 updates) directly impacted NVIDIA, ASML, Tokyo Electron, and the entire semiconductor supply chain. EU AI Act, DMA/DSA, and US antitrust actions against Google, Apple, and Amazon create material earnings risk for companies that represent 20%+ of S&P 500 market cap. This is not a niche regulatory issue — it is a first-order driver of the largest companies in the world.

---

### Category 4: Rates & Credit (10 Factors)

**Why this category exists:** The bond market is the largest financial market in the world. US Treasuries are the global risk-free rate. Credit spreads are the market's real-time assessment of corporate default risk. The yield curve is the most reliable recession predictor in existence. This category is the transmission mechanism between monetary policy and the real economy — when the Fed raises rates, it's the bond market that *implements* the tightening by repricing mortgages, corporate bonds, and government borrowing costs.

**28-30. US 2Y, 10Y, and 30Y Treasury Yields**
We monitor three points on the curve because they respond to different forces. The 2Y is tethered to Fed policy expectations (it's "the market's guess at the next 2 years of fed funds"). The 10Y is the global benchmark that prices mortgages, investment-grade corporates, and EM debt. The 30Y is driven by long-run inflation expectations, pension demand, and fiscal sustainability concerns. In 2022, the 2Y moved first (rate hikes expected), then the 10Y followed, then the 30Y lagged — the sequence told you the tightening was being driven by policy, not by inflation expectations unanchoring. Monitoring all three points gives us the *shape* of the story.

**31. Yield Curve Spread (10Y-2Y)**
The most famous recession indicator in finance. Every US recession since 1955 was preceded by yield curve inversion (10Y below 2Y). The curve inverted in July 2022 and stayed inverted for over two years — the longest inversion on record. We include it as a standalone factor because the *spread itself* is a causal driver: it affects bank profitability (banks borrow short and lend long), credit creation incentives, and market risk appetite. A deeply inverted curve tells banks that lending is unprofitable, which reduces credit supply to the real economy.

**32-33. Investment Grade and High Yield Credit Spreads**
Credit spreads are the market's real-time assessment of corporate default risk — more responsive than rating agency opinions, more granular than equity prices. IG spreads widen in slowdowns (companies with strong balance sheets still face higher borrowing costs). HY spreads blow out in crises (weak companies face potential default). The IG-HY spread differential tells you whether stress is broad-based or concentrated in weak credits. In the 2020 COVID selloff, HY spreads hit 1100bp — meaning the market was pricing a wave of defaults that ultimately didn't materialize (because the Fed stepped in to buy corporate bonds for the first time). We need both IG and HY because they tell different stories.

**34. US 10Y Real Yield (TIPS)** *(NEW)*
We include this because it is arguably **the single most important price in global finance** and our system was completely blind to it. The 10Y TIPS yield is the *real* discount rate — the return investors earn after inflation. When real yields are negative (as they were from 2020-2022), investors are *paying* for the privilege of lending to the government in real terms, which pushes them into risk assets (equities, crypto, venture capital). When real yields rose from -1.0% to +2.5% in 2022, it repriced every long-duration asset on the planet. The NASDAQ fell 33%. Crypto fell 75%. Venture valuations collapsed. ARK Innovation fell 80%. All of this was the *same trade* — a repricing of the real discount rate. A macro system without real yields is like a cockpit without an altimeter.

**35. 10Y Breakeven Inflation** *(NEW)*
We include this because **breakevens are the market's inflation expectations**, and when expectations unanchor, the regime changes entirely. Breakevens collapsed from 1.8% to 0.5% in March 2020, signaling the market expected *deflation* — this triggered the most aggressive monetary easing in history. Breakevens then rose to 3.0% by April 2022, signaling the market believed inflation was persistent — this validated the Fed's hawkish pivot. The spread between actual CPI and breakevens tells you whether the market believes the Fed has inflation under control. If breakevens surge above 3.5%, the Fed will have to tighten regardless of employment — and that changes the entire macro playbook.

**36. 5Y5Y Forward Inflation** *(NEW)*
We include this because it is the **Fed's own preferred measure of long-run inflation anchoring.** The 5Y5Y forward strips out near-term inflation noise and tells you what the market expects inflation to average from 5 years from now to 10 years from now. If this deviates materially from 2%, the Fed's credibility is in question. Chair Powell has repeatedly cited this measure in press conferences. It has remained remarkably stable at 2.0-2.5% through the entire inflation episode — the fact that it *didn't* unanchor is a key reason the Fed was ultimately able to bring inflation down without a recession. If it had unanchored, the Fed would have had to induce a Volcker-style recession.

**37. EM Sovereign Spread (EMBI)** *(NEW)*
We include this because **emerging market debt distress is a recurring crisis that our system had no way to detect.** The EMBI spread captures aggregate EM credit risk — the premium investors demand for holding EM sovereign debt over US Treasuries. It blew out during the 2013 Taper Tantrum (+200bp in 3 months), the 2018 Turkey/Argentina crisis, the 2020 COVID panic, and every strong-dollar episode. EM sovereign defaults cascade into EM banking systems, EM currencies, and EM equity markets — and from there into developed market banks with EM exposure and commodity markets. Without this factor, we cannot detect or propagate EM contagion.

---

### Category 5: Volatility (6 Factors)

**Why this category exists:** Volatility is not just a risk metric — it is a *causal force*. When the VIX spikes, it triggers forced selling by volatility-targeting strategies, margin calls on leveraged positions, and option dealer hedging flows that amplify market moves. Volatility regimes determine whether a 1% equity decline is a buying opportunity or the start of a 20% crash. We monitor multiple volatility measures because equity vol, bond vol, and FX vol often diverge — and the divergences tell you which market is mispricing risk.

**38. VIX**
The "fear gauge." S&P 500 30-day implied volatility. We include it not because it predicts crashes (it doesn't — it reacts to them), but because VIX *level* determines the behavior of $500B+ in volatility-targeting and risk-parity strategies. These strategies mechanically sell equities when VIX rises and buy when VIX falls. A VIX move from 15 to 25 triggers billions of dollars in forced equity selling, creating a self-reinforcing feedback loop. The VIX is not just measuring fear — it is *creating* it.

**39. MOVE Index**
Bond market volatility. We include this separately from VIX because **when rates are volatile, everything is volatile.** The MOVE index hit all-time highs during the 2023 SVB crisis and the 2022 UK gilt crisis (Truss mini-budget). High MOVE means banks cannot reliably hedge their Treasury portfolios, which was literally the mechanism that killed SVB (unrealized losses on held-to-maturity bonds). MOVE also correlates with reduced market-making capacity in Treasuries, which means bond markets become less liquid precisely when they're most volatile — a dangerous feedback loop.

**40. Put/Call Ratio**
Options market positioning. Extreme readings are contrarian indicators: very high put/call ratios signal capitulation (too much hedging, market may bottom), very low ratios signal complacency (no one is hedging, market is vulnerable). We use this as a sentiment gauge rather than a timing tool — it tells us where the market *believes* risk is, not where risk actually is.

**41. SKEW Index**
Tail risk pricing. SKEW measures the cost of out-of-the-money put options relative to at-the-money options. High SKEW = the market is pricing crash risk even while VIX is low. This divergence (low VIX + high SKEW) was present before the February 2018 "Volmageddon" crash. It tells you that the *surface* is calm but someone is paying up for catastrophe insurance.

**42. Credit Default Swaps**
Market-priced credit risk at the entity level. CDS spreads react faster than bond spreads because the CDS market is more liquid and can be traded on margin. In 2023, Credit Suisse CDS blew out weeks before the bank actually collapsed. CDS-bond basis (the gap between CDS-implied spread and cash bond spread) blowing out signals *funding stress* — the kind of plumbing problem that indicates systemic risk.

**43. FX Implied Volatility** *(NEW)*
We include this because **currency volatility often leads equity and bond volatility.** The August 2024 yen carry unwind was a *currency* event that cascaded into global equity markets. The 2022 UK gilt crisis started as a *GBP* event (cable dropped 10% in days). EM crises always manifest in FX vol first. Our system had equity vol (VIX) and bond vol (MOVE) but no FX vol — meaning we'd detect the cascade after it had already spread to our monitored markets, rather than when it originated.

---

### Category 6: Commodities (10 Factors)

**Why this category exists:** Commodities are the physical inputs to the global economy. Oil prices determine transportation and heating costs for every person on the planet. Copper demand tells you whether the world is building or contracting. Agricultural prices determine whether emerging market populations can afford to eat, which determines political stability, which determines geopolitical risk. Commodities are also the transmission mechanism for many geopolitical shocks — Russia-Ukraine affected the world primarily through energy and food prices, not through direct financial linkages.

**44. WTI Crude Oil**
The single most important commodity. Oil affects CPI (directly and via transportation costs), consumer spending (gas prices), corporate margins (input costs), geopolitical dynamics (petrostates), and central bank reaction functions (core vs. headline inflation). OPEC+ production decisions, US shale response, and strategic reserve releases are all policy levers that interact with demand cycles. Oil going negative in April 2020 was arguably the most extraordinary price event in financial history.

**45. Gold**
The oldest safe haven. Gold trades as an inverse function of real yields (when real yields fall, gold rises — because the opportunity cost of holding a non-yielding asset decreases). But gold also responds to central bank reserve diversification (China and EM central banks have been accumulating gold as a hedge against US financial sanctions), geopolitical risk, and dollar weakness. Gold broke above $2,000/oz permanently in 2024, driven by the combination of central bank buying and real rate expectations.

**46. Copper**
"Dr. Copper" — the metal with a PhD in economics. Copper is used in construction, electronics, EVs, and power infrastructure. Its price is the most reliable real-time gauge of global industrial activity. Copper collapsed 40% in the 2008 GFC before equities did. It surged 100% in 2020-21 as China stimulus kicked in. The green energy transition is adding a structural demand component (EVs use 4x more copper than ICE vehicles), which means copper supply constraints are now a macro factor, not just a mining story.

**47. Natural Gas**
The 2022 European energy crisis demonstrated that natural gas is a **distinct macro factor from oil.** European gas prices rose 10x, causing industrial production collapse in Germany, fertilizer plant shutdowns globally, and a direct hit to European GDP. The LNG trade rerouting (US → Europe instead of Asia) affected Asian energy costs. Natural gas matters for electricity generation, heating, and as a feedstock for fertilizers — making it a transmission mechanism from geopolitics to food prices.

**48. Silver**
A hybrid precious/industrial metal. Silver tracks gold (safe haven) but also has industrial demand from solar panels, electronics, and EVs. We include it at lower priority because it provides a second signal on the gold narrative with an industrial overlay — when silver outperforms gold, it suggests the rally is driven by industrial demand rather than pure fear.

**49. Wheat**
The food inflation bellwether. Russia and Ukraine together supply ~30% of global wheat exports. The 2022 invasion caused wheat to surge 60% in days, triggering food inflation in emerging markets and political instability (Sri Lanka, Egypt). Wheat prices affect CPI in EM economies far more than in developed markets — a wheat price spike in the US is an inconvenience, but in Egypt it's a revolution.

**50. Soybeans** *(NEW)*
We include this because soybeans are the **single best barometer of US-China agricultural trade.** China is the world's largest soybean importer, and the US is a top exporter. When China imposed retaliatory tariffs on US soybeans in 2018, it was the clearest signal that the trade war was escalating. Soybean prices are also linked to biofuel policy, South American weather, and global protein demand. This factor gives us visibility into the agricultural dimension of trade conflict and emerging market food security.

**51. Iron Ore** *(NEW)*
We include this because iron ore is the **highest-fidelity indicator of China's construction and infrastructure activity** — more sensitive than copper, more specific than PMI. When China stimulates, iron ore rallies first. When China's property sector collapses (as in 2021-23), iron ore falls first. The price went from $220 to $80 as the Evergrande crisis unfolded, signaling the severity of the property downturn months before Chinese official data confirmed it. Iron ore is how the commodity market tells you the truth about China when official statistics won't.

**52. Lithium** *(NEW)*
We include this at lower priority because lithium price dynamics reveal the health of the **EV supply chain and green energy transition.** Lithium's 80% price crash in 2023 signaled that EV demand growth was decelerating and supply was catching up — a narrative shift that repriced the entire EV supply chain (Tesla, battery makers, mining companies). Lithium supply is geopolitically concentrated (Australia, Chile, China refining), creating a strategic mineral risk similar to semiconductors.

**53. Uranium** *(NEW)*
We include this at lower priority because the **nuclear renaissance narrative** — driven by AI data center power demand, net-zero targets, and energy security concerns — is emerging as a macro theme. Uranium supply is structurally constrained (underinvestment since Fukushima), and the demand catalyst (AI power consumption) is growing exponentially. This is a building structural risk rather than a current market mover, but its inclusion allows us to track the energy-AI nexus.

---

### Category 7: Equities (13 Factors)

**Why this category exists:** Equity markets are where most of the world's wealth is allocated and where macro forces become visible to the broadest audience. But "the stock market" is not one thing — the S&P 500, NASDAQ, Russell 2000, EM equities, and Chinese equities often move in different directions because they are driven by different macro factors. A rising S&P 500 alongside falling EM equities tells you the move is driven by US exceptionalism and dollar strength. A rising NASDAQ alongside falling Russell 2000 tells you it's a narrow AI/tech rally, not a broad growth story. We need granularity.

**54-55. S&P 500 and NASDAQ**
The two benchmark US indices. S&P is the broad market; NASDAQ is the growth/tech proxy. Their divergence is informative: in 2022, NASDAQ fell 33% while S&P fell 19% — the gap told you the selloff was driven by rate sensitivity (long-duration growth stocks repriced more). In 2024, NASDAQ outperformed by 10%+ — the gap told you the rally was narrow (AI/Magnificent 7). We need both to decompose what's driving US equity performance.

**56. Tech Sector**
Tech is 30%+ of S&P 500 market cap. It deserves standalone monitoring because tech has *distinct* macro drivers: rate sensitivity (long-duration cash flows), AI capex cycle, chip supply chains, regulatory risk, and advertising revenue (consumer economy proxy). When tech leads or lags the market, it tells you something about which macro factor is dominant.

**57. Energy Sector**
Energy equities are the equity market's proxy for oil prices, but with leverage. They also function as an inflation hedge — energy stocks rallied 65% in 2022 while the S&P fell. This makes them an important portfolio composition signal: when energy leads, the market is pricing persistent inflation and commodity strength.

**58. Financials Sector**
Banks are the transmission mechanism of monetary policy. When the Fed hikes, bank net interest margins should expand (they did in 2022-23). When the yield curve inverts, bank profitability compresses (it did, and SVB collapsed). Financial sector performance tells you whether rate policy is being successfully transmitted or is creating stress in the banking system.

**59. Russell 2000**
Small-cap equities are more sensitive to domestic economic conditions (less international revenue), more sensitive to interest rates (more floating-rate debt), and more sensitive to credit conditions (less access to bond markets, more dependent on bank lending). The Russell 2000 underperformed the S&P by 30%+ from 2022-2024, telling you that the *average* US company was struggling even as mega-cap tech surged. It's the health check for the real US economy.

**60. Healthcare Sector** *(NEW)*
We include this because healthcare is a **defensive sector with distinct macro drivers** that provide signal about risk appetite and policy risk. When healthcare outperforms (2022 bear market), it signals defensive positioning. Drug pricing legislation, ACA repeal risk, Medicare negotiation authority, and biotech funding cycles are all distinct macro factors. Healthcare's relative performance is one of the cleanest signals of market risk appetite.

**61. REITs** *(NEW)*
We include this because REITs are the **only real-time, liquid proxy for commercial real estate values** — a $20T+ market that is otherwise opaque. The office vacancy crisis (20%+ in many cities), the "work from home" structural shift, and the rate sensitivity of property valuations are all visible in REIT prices. REITs fell 30%+ from 2022-2023 while official CRE valuations barely moved — the market was pricing the crisis that appraisals refused to acknowledge. Without REITs, we have no real-time signal on one of the largest asset classes in the world.

**62. Regional Banks** *(NEW)*
We include this because the **2023 SVB crisis proved that regional banks are a distinct systemic risk factor.** Large-cap financials (XLF) fell 10% during SVB; regional banks (KRE) fell 35%. The risk was concentrated: CRE exposure, held-to-maturity bond losses, uninsured deposit concentration, and technology/VC client concentration. These risks are invisible in a broad "financials sector" node. Regional banks also control the majority of CRE lending, small business lending, and agricultural lending — making them the credit pipeline for the real US economy outside the S&P 500.

**63. EM Equities** *(NEW)*
We include this because **emerging markets are a distinct asset class driven by factors our system now captures.** EM equities are driven by: DXY (strong dollar = weak EM), China growth (China is the largest EM economy and the largest trade partner for most EM countries), commodity prices (many EM economies are commodity exporters), and EM-specific risk (political instability, policy errors, debt sustainability). Without EM equities, we can observe that DXY is strengthening but we cannot trace the *consequence* — which is capital fleeing EM and EM equities selling off.

**64. European Equities** *(NEW)*
We include this because Europe is driven by **distinct macro factors** that diverge from the US. The 2022 energy crisis was a Europe-specific event (gas dependence on Russia). ECB policy diverges from the Fed. European exporters (luxury goods, industrials, autos) have China exposure that US companies don't. The European banking system has different risk characteristics (Deutsche Bank, Credit Suisse). European equity performance gives us a window into these factors.

**65. China Equities** *(NEW)*
We include this because **China's equity market moves independently of global factors** — driven by PBOC policy, regulatory crackdowns (2021 tech crackdown erased $1T), property crisis dynamics, and stimulus announcements. China equities fell 60% from peak while US equities hit all-time highs — a divergence that no US-centric model would have predicted or explained. China equities also serve as a leading indicator for EM equities and commodity demand.

**66. Semiconductors** *(NEW)*
We include this because semiconductors are **the most strategically important industry in the world today**, at the intersection of three macro forces: AI capex (NVIDIA revenue grew from $27B to $60B in one year), geopolitical competition (US-China chip export controls), and cyclical sensitivity (memory chips are one of the most cyclical industries). The SOX semiconductor index often leads the NASDAQ by 1-3 months. Without a semiconductor node, we cannot trace the AI boom or the chip war — two of the defining macro themes of 2023-2025.

---

### Category 8: Equity Fundamentals (5 Factors)

**Why this category exists:** Prices can deviate from fundamentals for years, but eventually earnings, valuations, and margins *matter*. When the S&P 500 trades at 22x forward earnings with a 2.5% real yield, the equity risk premium is near zero — meaning stocks offer no excess compensation for risk. That is a regime-defining signal that affects expected returns for every allocator in the world.

**67. Earnings Momentum**
Earnings revision breadth — the percentage of companies seeing upward vs. downward revisions. This is a leading indicator for actual earnings (and therefore equity returns). Momentum shifted negative in Q3 2022 (signaling the earnings recession) and positive in Q1 2023 (signaling recovery). It moves before earnings are reported.

**68. P/E Valuations**
Forward P/E ratio for the S&P 500. Not a timing tool, but a *vulnerability* indicator. At 22x earnings, a 10% earnings miss or a 50bp rise in real yields can cause a 15%+ drawdown. At 15x, the same shock causes a 5% dip. Valuations determine the *severity* of selloffs, not their timing.

**69. Revenue Growth**
Top-line growth is harder to engineer through buybacks, accounting, or margin expansion. When revenue growth decelerates, it signals genuine demand weakness rather than financial engineering running out of road. Revenue growth turned negative in Q1 2023 for the first time since COVID, correctly signaling the manufacturing recession.

**70. Equity Risk Premium** *(NEW)*
We include this because it is the **single number that tells you whether equities are attractive relative to bonds.** Defined as earnings yield (1/PE) minus real yield (TIPS). When the ERP is 5%+ (as in 2009, 2020), stocks are being given away relative to bonds. When it's near zero (as in late 2023, early 2024), there is no compensation for owning equities over the risk-free asset. This measure collapsed from 4%+ in 2020 to near zero in 2024, which is why the "higher for longer" regime is so dangerous for equities — bonds became competitive for the first time in 15 years. Every asset allocator in the world is watching this number.

**71. Corporate Buybacks** *(NEW)*
We include this because buybacks are the **single largest source of US equity demand** — roughly $1 trillion per year for S&P 500 companies. When buybacks are running (most of the year), they provide a bid under the market. When they stop (earnings blackout windows, credit tightening, tax policy changes), the bid disappears. The 2019 proposal to tax buybacks and the 2022 1% excise tax both moved markets. Buyback activity is also a signal of corporate confidence: companies buy back stock when they believe their shares are cheap and their future is bright.

---

### Category 9: Currencies (7 Factors)

**Why this category exists:** Currencies are the relative price of one country's monetary policy, growth, and risk against another's. They are also the *mechanism* through which US monetary policy is exported to the world. When the Fed hikes and the dollar strengthens, every country with dollar-denominated debt faces tighter financial conditions regardless of their own central bank's actions. The dollar is the world's reserve currency, and DXY strength/weakness is a global financial conditions indicator.

**72. US Dollar Index (DXY)**
The single most important currency indicator. DXY strength correlates with: tighter global financial conditions, weaker commodities, weaker EM assets, and compressing US multinational earnings (translation effect). DXY weakening correlates with: easier global conditions, commodity rallies, EM equity outperformance. The 2022 DXY surge (to 20-year highs) was the mechanism through which US rate hikes were transmitted globally.

**73-75. EUR/USD, USD/JPY, USD/CNY**
The three most systemically important bilateral exchange rates. EUR/USD — ECB vs. Fed policy divergence, European economic health, energy security. USD/JPY — carry trade dynamics, BOJ policy, Japan's $1.3T in US Treasury holdings. USD/CNY — trade tensions, China's managed exchange rate as a policy tool, capital flow signal. Each pair has a distinct driver set and a distinct contagion pathway.

**76. GBP/USD** *(NEW)*
We include this because the UK is a **distinct macro entity with its own crisis dynamics.** The September 2022 "Truss mini-budget" crashed GBP by 10% in days and triggered a pension fund liquidity crisis that forced the BOE to intervene. Brexit created permanent trade friction. The BOE's divergence from the Fed (cutting while the Fed was on hold, or vice versa) creates distinct GBP dynamics. As a G10 reserve currency, GBP distress is a signal of broader "fiscal credibility" risk — if it can happen to the UK, markets ask whether it can happen to others.

**77. EM FX Basket** *(NEW)*
We include this because **EM currency stress is the first signal of EM crisis.** Before EM sovereign spreads blow out, before EM equities crash, EM currencies weaken. The Turkish lira's 50% collapse preceded Turkey's inflation and banking crisis. The Argentine peso's crawling peg break preceded the sovereign default. An aggregate EM FX basket captures the collective stress across dozens of EM economies, weighted by importance. This is the early warning system for EM contagion.

**78. Bitcoin** *(NEW)*
We include this because Bitcoin is now a **$1 trillion+ asset class with material institutional adoption.** The launch of spot Bitcoin ETFs in January 2024 brought $50B+ in flows, making Bitcoin allocation decisions relevant for mainstream asset managers. Bitcoin's correlation regime shifts: in risk-on environments, it trades like "leveraged NASDAQ" (correlated with tech); in dollar-weakness environments, it trades like "digital gold" (correlated with gold and inverse DXY); in liquidity crises, it crashes alongside all risk assets. Bitcoin is also a proxy for global liquidity conditions and speculative risk appetite. A macro system ignoring a $1T+ asset that institutional investors now hold is willfully blind.

---

### Category 10: Flows & Sentiment (5 Factors)

**Why this category exists:** Fundamentals tell you what *should* happen. Flows and positioning tell you what *is* happening and what *will* happen mechanically. If every hedge fund is long the same trade and the trade goes against them, the forced selling creates a crash regardless of fundamentals. The Yen carry trade unwind in August 2024 was a *positioning* event, not a fundamental event — and it caused a 12% crash in Japanese equities and a 3% drop in the S&P in a single day.

**79. Retail Sentiment**
Social media, survey-based, and options flow indicators of retail investor behavior. Retail sentiment is a contrarian indicator at extremes: when retail is euphoric (crypto in November 2021, meme stocks in January 2021), markets are near tops. When retail capitulates (December 2022 crypto, March 2020 equities), markets are near bottoms. The signal is in the extremes, not the level.

**80. Fund Flows**
Net flows into equity, bond, and money market funds. Tells you what investors are actually *doing* with their money (vs. what surveys say they're thinking). The rotation from money market funds back into equities in late 2023 was a key driver of the Q4 rally. Record flows out of bond funds in 2022 amplified the selloff.

**81. Institutional Positioning (COT)**
CFTC Commitment of Traders data. Shows net speculative positioning in futures markets. When speculators are max long equities and max short bonds, the *mechanical* risk is a reversal — any shock forces position unwinds that amplify the move. The August 2024 yen carry unwind was partially caused by *extreme* speculative short JPY positioning unwinding simultaneously.

**82. Margin Debt / Leverage** *(NEW)*
We include this because **leverage is the amplifier that turns corrections into crashes.** FINRA margin debt peaked at $936B in October 2021 — the same month as the market top. Margin calls force selling, which causes more margin calls, which forces more selling. This is the self-reinforcing feedback loop that turned the 2020 COVID selloff into a -34% crash in 23 trading days. Separately, total system leverage (including options, futures, and prime brokerage lending) determines how fragile the market is to shocks. A 2% correction in a low-leverage regime is a buying opportunity. A 2% correction in a high-leverage regime is a potential crash trigger.

**83. ETF Flows** *(NEW)*
We include this because **passive investing has fundamentally changed market structure.** Over 50% of US equity assets are now in passive/index vehicles. ETF creation and redemption flows mechanically move underlying stock prices — when $1B flows into SPY, it buys every S&P 500 stock proportionally regardless of valuation. This creates momentum effects (inflows beget price increases beget more inflows), concentration risk (the biggest stocks get the biggest flows), and correlation risk (all stocks in an index move together). ETF flow data tells us whether the "passive bid" is supporting or withdrawing from the market.

---

### Category 11: Global (8 Factors)

**Why this category exists:** The US is 26% of global GDP but 60%+ of global equity market cap. This means our US-centric categories above describe the dominant financial market, but not the dominant economy. China's 18% of global GDP, the Eurozone's 15%, India's growing share, and the collective EM 40%+ share drive commodity demand, supply chain dynamics, and global growth expectations. A US-only macro model would have missed the 2011 European debt crisis, the 2015 China devaluation, and the 2022 European energy crisis.

**84. China PMI**
China is the world's manufacturing floor. China PMI leads global trade volumes, commodity demand, and EM growth expectations. A move from 49 to 52 in China PMI is a more powerful global growth signal than a move from 52 to 55 in US PMI — because China's marginal commodity consumption is massive.

**85. EU HICP**
Eurozone inflation drives ECB policy, which drives EUR/USD, which drives global dollar conditions. EU HICP hit 10.6% in October 2022 (driven by energy), forcing the ECB to hike aggressively even as the European economy contracted — a "stagflation" dynamic unique to Europe.

**86. BOJ Policy**
Japan is the world's largest creditor nation with $3.1T in foreign assets. BOJ yield curve control kept Japanese 10Y yields near 0% for years, driving a massive carry trade (borrow in JPY, invest in higher-yielding assets globally). When the BOJ loosened YCC in 2023 and raised rates in 2024, it triggered the yen carry unwind — the most violent single-day equity move of 2024. BOJ policy changes have outsized global impact because of Japan's accumulated foreign positions.

**87. China Credit Impulse** *(NEW)*
We include this because the China credit impulse — the change in total social financing as a percentage of GDP — is **the single best leading indicator for global industrial activity.** It leads global PMIs by 6-9 months. It leads commodity prices. It leads EM equity performance. The mechanism is direct: when Chinese banks and shadow banks extend more credit, that credit funds construction, infrastructure, and manufacturing expansion, which drives demand for iron ore, copper, oil, and every other industrial commodity. The credit impulse turned negative in late 2021, correctly predicting the global manufacturing slowdown that followed. Without this factor, we cannot forecast the direction of global growth.

**88. China Property Sector** *(NEW)*
We include this because China's property sector is approximately **30% of GDP** (including related industries), and its crisis is the largest ongoing structural risk in the global economy. Evergrande's default in 2021, Country Garden's collapse in 2023, and the ongoing developer debt restructuring have destroyed household wealth (70%+ of Chinese household assets are in property), depressed consumer confidence, and created deflationary pressure. The property crisis cascades through: iron ore (construction demand), copper (wiring), Australian dollar (mining exports to China), and global growth expectations. Our system previously had no way to monitor this — the most important single-sector risk in the world economy.

**89. EU Periphery Spreads (Italy-Germany)** *(NEW)*
We include this because the **Eurozone fragmentation risk is existential and recurring.** The Italy-Germany 10Y spread measures whether the market believes the Eurozone will stay together. When it blew out to 550bp in 2011, the Euro nearly collapsed. When it spiked in 2018 (Italian budget crisis) and 2022 (ECB tightening), the ECB had to invent new tools (TPI) to contain it. This spread is the barometer of European institutional credibility. If it goes above 300bp, the ECB is forced into crisis mode regardless of inflation, and EUR/USD collapses — making it a first-order macro driver.

**90. Global Trade Volume** *(NEW)*
We include this because **trade contraction has preceded every global recession since WWII.** The WTO/CPB world trade monitor captures the volume of goods crossing borders — stripped of price effects. Trade volume collapsed 15% in 2020 (COVID), declined in 2019 (tariff war), and is under pressure again in 2025 (new tariff escalation). For export-dependent economies (Germany, Japan, South Korea, most of EM), trade volume is more important than US GDP growth. It also serves as a real-time check on whether tariff policies are actually reducing trade or merely rerouting it.

**91. India Growth** *(NEW)*
We include this because India is the **5th largest economy and the fastest-growing major economy**, projected to become the 3rd largest by 2028. India's growth drives distinct commodity demand (especially oil — India is the 3rd largest importer), technology services demand, and an emerging consumer market. India's economic trajectory is increasingly relevant for global allocators: MSCI recently increased India's weight in EM indices, and foreign institutional flows into India are becoming material. This factor also captures the "China+1" supply chain diversification theme.

---

### Category 12: Housing / Real Estate (4 Factors) — NEW

**Why this category exists:** The 2008 Global Financial Crisis — the worst financial disaster since the Great Depression — was a **housing** crisis. The entire global financial system nearly collapsed because of US residential mortgage defaults. And yet, our factor graph had zero housing factors. Housing is the most interest rate-sensitive sector of the economy, the largest component of household wealth (65%+ for median households), and the largest component of CPI (shelter inflation is 40% of CPI). Any macro surveillance system without housing is like a fire alarm with no smoke detector.

**92. US Housing Starts** *(NEW)*
We include this because housing starts are the **most interest rate-sensitive leading indicator of economic activity.** When mortgage rates doubled from 3% to 7% in 2022, housing starts dropped 25% — the fastest decline since 2008. Housing construction drives employment (residential construction is 3-4% of GDP), materials demand (lumber, copper, concrete), and GDP. Starts lead GDP by 2-3 quarters because a house that breaks ground today generates economic activity for 6-12 months.

**93. US Home Prices (Case-Shiller)** *(NEW)*
We include this because home prices are the **primary transmission mechanism of the wealth effect** — when home prices rise, homeowners feel wealthier and spend more. US residential real estate is worth ~$45 trillion, making it the largest asset class in the world. Home prices also *directly* feed into CPI via shelter/rent inflation (owners' equivalent rent is 26% of CPI). The 2006-2012 home price decline of 27% destroyed $7 trillion in household wealth and triggered the GFC. The 2020-2022 surge of 40% created a wealth effect that helped sustain consumer spending even as the Fed tightened. You cannot model US inflation or US consumption without modeling home prices.

**94. 30-Year Mortgage Rate** *(NEW)*
We include this because mortgage rates are the **direct transmission mechanism from Fed policy to housing activity and consumer spending.** The mortgage rate moved from 2.65% (January 2021) to 7.79% (October 2023) — a tripling that had never happened before in such a short period. This made monthly payments on a median-priced home 60% more expensive, freezing the existing home market (homeowners refused to sell and give up their 3% mortgages) while crushing new home affordability. The "mortgage rate lock-in" effect is constraining labor mobility, housing supply, and household formation. This is the most consequential Fed transmission channel for the average American.

**95. Commercial Real Estate Stress** *(NEW)*
We include this because CRE is the **slow-moving crisis that the financial system is struggling to acknowledge.** Office vacancy rates are above 20% in major cities. Work-from-home is a permanent structural shift, not a pandemic anomaly. CRE loans represent 30% of regional bank assets — the same banks that nearly failed during SVB. CRE valuations are marked at appraisal values that lag market reality by 12-18 months. The disconnect between market prices (REIT indices down 30%+) and bank book values (barely marked down) is a solvency illusion. When the "extend and pretend" strategy on CRE loans expires (most loans are 5-7 year term), banks will face realized losses. This is the risk that kept the 2023 banking crisis from being declared "over."

---

### Category 13: Financial System / Banking (4 Factors) — NEW

**Why this category exists:** The financial system is the **plumbing** of the economy. When plumbing works, no one thinks about it. When it fails, everything stops. The 2008 GFC, the 2019 repo crisis, the 2020 COVID liquidity crunch, and the 2023 SVB collapse were all *plumbing* failures. Yet our system had no visibility into bank lending conditions, reserve levels, funding stress, or aggregate financial conditions. We were monitoring the house's temperature (inflation, GDP) without checking whether the pipes were frozen.

**96. Financial Conditions Index** *(NEW)*
We include this because the Chicago Fed National Financial Conditions Index is the **single best aggregate measure of whether financial conditions are loose or tight.** It integrates 105 indicators: interest rates, credit spreads, equity prices, dollar strength, money supply, bank lending, and volatility into one number. When the FCI tightens rapidly (as in Q4 2018, March 2020, Q3 2022), risk assets sell off. When it loosens (as in Q4 2023), risk assets rally. Fed officials watch the FCI to gauge whether their rate hikes are *actually* tightening conditions — because sometimes the market rallies through rate hikes (2023), effectively loosening conditions and undermining the Fed's intentions.

**97. Bank Lending Standards** *(NEW)*
We include this because the Fed Senior Loan Officer Opinion Survey (SLOOS) is the **most reliable predictor of credit availability to the real economy.** When banks tighten lending standards, businesses can't get loans, consumers can't get mortgages, and economic activity contracts — regardless of what the Fed funds rate is. Tightening lending standards preceded every US recession since 1990. After SVB, bank lending standards tightened to GFC levels — equivalent to ~50bp of additional rate hikes that the Fed didn't have to implement. This is the "shadow tightening" that models miss if they only watch the fed funds rate.

**98. Bank Reserves at the Fed** *(NEW)*
We include this because reserve adequacy determines whether **the money market plumbing functions or seizes.** In September 2019, the repo market blew up (overnight rates spiked from 2% to 10%) because the Fed had drained reserves too far via QT. The Fed had to emergency-inject $75B/day to stabilize the system. As QT continues in 2024-25, the question is: when do reserves again hit the "scarcity" threshold? If the answer is "unexpectedly," we get another plumbing crisis. Monitoring reserves allows us to estimate the proximity of this cliff.

**99. Repo / SOFR Rate** *(NEW)*
We include this because SOFR (Secured Overnight Financing Rate) is the **heartbeat of the financial system.** It replaced LIBOR as the benchmark for $400T+ in financial contracts. When SOFR is stable and close to the fed funds rate, the plumbing is healthy. When SOFR spikes above the fed funds rate, it signals funding stress — banks or institutions are willing to pay a premium for overnight cash, which means someone is in trouble. The September 2019 repo crisis was visible in SOFR days before the Fed acknowledged it. March 2020 saw SOFR dislocations before the Fed's emergency interventions. This is our real-time stress sensor for the financial plumbing.

---

### Category 14: Money Markets / Funding (3 Factors) — NEW

**Why this category exists:** Money markets are where the financial system funds itself *overnight*. When money markets work, no one outside of fixed income trading desks cares. When they freeze, the financial system dies within days. The commercial paper market freezing in September 2008 is what turned a housing crisis into a global financial crisis — companies like GE could not roll their short-term debt. The Fed's emergency facilities in 2020 (CPFF, PDCF, MMLF) were all designed to unfreeze money markets. This is a distinct category from "Financial System" because money market stress operates on a different timescale (days, not months) and requires different interventions.

**100. TED Spread (SOFR-Treasury)** *(NEW)*
We include this because the TED spread (modernized as SOFR minus T-bill) is the **fastest real-time indicator of counterparty and funding stress.** It measures how much more banks charge each other for unsecured lending compared to lending to the US government. During the GFC, TED spread hit 450bp (banks didn't trust each other). During COVID, it spiked to 140bp. During SVB, it jumped 50bp in two days. A persistently elevated TED spread means the banking system is under stress — even if no individual bank has failed yet. It's the smoke detector for the next banking crisis.

**101. Money Market Fund Flows** *(NEW)*
We include this because money market funds are now a **$6 trillion+ force** that can destabilize the banking system through deposit competition. During the SVB crisis, $500B flowed from bank deposits into money market funds in a single week — the largest deposit migration in history. This happened because MMFs were yielding 5%+ while most banks were still paying 0.5% on deposits. The flow from deposits to MMFs is a form of bank disintermediation that tightens credit availability. It also means that money market fund *outflows* (back into equities or bank deposits) are a major source of liquidity that can fuel rallies.

**102. Commercial Paper Spread** *(NEW)*
We include this because commercial paper is how **large corporations fund their day-to-day operations** — payroll, inventory, working capital. When CP spreads widen, it means the market is pricing higher risk that these companies can't roll their debt. When the CP market *freezes* (as in September 2008 and briefly in March 2020), companies face immediate liquidity crises regardless of their long-term solvency. The Fed created the Commercial Paper Funding Facility specifically because CP market dysfunction threatened to turn a financial crisis into an immediate corporate bankruptcy wave.

---

### Category 15: Fiscal Policy / Sovereign (3 Factors) — NEW

**Why this category exists:** We are living through the most aggressive fiscal expansion in peacetime history. The combination of COVID stimulus ($5T+), infrastructure spending ($1.2T), CHIPS Act ($280B), and IRA ($370B) has fundamentally altered the US fiscal trajectory. Fiscal deficits running at 6%+ of GDP during full employment are historically unprecedented. This has real consequences: more Treasury issuance, higher term premium, and a credibility question about long-run fiscal sustainability. The 2023 bond selloff was *primarily* about fiscal concerns, not inflation. A macro system that only watches the Fed but ignores Congress is missing half the policy picture.

**103. US Debt-to-GDP** *(NEW)*
We include this because **fiscal sustainability is a structural risk that constrains future policy options.** US federal debt exceeded 120% of GDP in 2024 — the highest since WWII. At current trajectory, interest payments will exceed defense spending by 2025. This matters because: (a) it limits the government's ability to stimulate during the next recession (fiscal space is constrained), (b) it raises questions about long-run dollar reserve currency status, and (c) it creates a self-reinforcing dynamic where higher rates → higher interest payments → larger deficits → more issuance → higher rates. We monitor this as a slow-moving structural constraint that defines the policy envelope.

**104. Treasury Issuance / Supply** *(NEW)*
We include this because **Treasury supply directly moves bond prices**, and the supply shock of 2023 was the proximate cause of the 10Y yield hitting 5%. When the Treasury refunding announcement in August 2023 revealed larger-than-expected issuance, yields rose 100bp in weeks. The market was asking: "who will buy an extra $1 trillion in Treasuries per year?" The answer was: "only at higher yields." This is a pure supply-demand dynamic that operates independently of monetary policy or inflation expectations. Net new Treasury supply is the marginal price setter for the world's risk-free rate.

**105. US Government Spending** *(NEW)*
We include this because the **fiscal impulse** (the change in government spending relative to GDP) is a major GDP growth driver that our system was ignoring. The IRA, CHIPS Act, and infrastructure bill collectively represent the largest US industrial policy since the Marshall Plan. Factory construction spending has doubled. Government contractors are on a hiring spree. This fiscal spending is one reason GDP growth remained robust despite 525bp of rate hikes — the government was stimulating while the Fed was braking. Without tracking government spending, our system attributes growth resilience entirely to consumer strength, missing the fiscal engine.

---

### Category 16: Supply Chain / Trade Infrastructure (3 Factors) — NEW

**Why this category exists:** The COVID pandemic taught the world that **supply chains are a macro force, not a logistics footnote.** Supply chain disruptions drove the 2021-22 inflation episode more than any demand-side factor. A single ship blocking the Suez Canal (March 2021) cost $10B/day in delayed trade. Houthi attacks in the Red Sea (2024) rerouted 30% of global container traffic. Semiconductor shortages shut down auto production lines worldwide. The lesson: supply chain disruptions transmit geopolitical shocks into inflation, corporate earnings, and GDP — and they can persist for years. A macro system without supply chain visibility is fighting the last war (demand-driven inflation of the 1970s) instead of the current one (supply-driven inflation of the 2020s).

**106. Supply Chain Pressure Index** *(NEW)*
We include this because the NY Fed Global Supply Chain Pressure Index is the **single best aggregate measure of supply chain stress.** It integrates shipping costs, delivery times, backlogs, and inventory data into one number. It peaked at 4.3 standard deviations above normal in December 2021 — the most extreme reading in its history. It then normalized through 2023, correctly signaling that goods inflation would decline. When Houthi attacks disrupted Red Sea shipping in late 2023, the index ticked back up, correctly signaling renewed supply-side inflation pressure. This factor is the bridge between geopolitics (the shock) and inflation (the consequence).

**107. Baltic Dry Index** *(NEW)*
We include this because the BDI is the **purest demand signal in commodity markets.** It measures the cost of shipping bulk commodities (iron ore, coal, grain) and is not subject to speculative trading (you can't go long the BDI for financial gain — it's a real cost of real shipping). The BDI collapsed 94% in 2008 before the recession was officially recognized. It surged in 2021 as China restocked. It is a leading indicator for global trade and industrial production, with a 1-2 month lead time.

**108. Container Shipping Rates** *(NEW)*
We include this because container rates are **distinct from bulk rates (BDI)** and capture consumer goods trade specifically. The Freightos/Drewry indices measure the cost of shipping a 40-foot container from Asia to US/Europe. These rates rose 10x during COVID (from ~$2K to $20K per container), directly adding 1-2% to US goods inflation. The Red Sea disruption in 2024 caused a 4x spike. Container rates feed directly into goods prices with a 2-3 month lag — making them one of the best real-time predictors of near-term goods inflation.

---

### Category 17: Private Credit / Alternatives (2 Factors) — NEW

**Why this category exists:** The financial system has fundamentally changed since the GFC. Bank lending has been constrained by regulation (Basel III, Dodd-Frank), and the gap has been filled by private credit — a $1.5 trillion+ market that has tripled since 2018. This market is opaque (no public pricing), illiquid (no secondary market), and concentrated (top 10 managers control 40%+ of assets). It is also providing the majority of leveraged lending to mid-market companies. If there is a credit cycle turn, private credit is where the stress will be *invisible* until it's too late to react. We include limited visibility here because we believe this is a structural risk building in the system.

**109. Private Credit / CLO Conditions** *(NEW)*
We include this because **private credit is the fastest-growing corner of the financial system and the least monitored.** CLO issuance (the primary funding mechanism) was $180B in 2023. Covenant quality has deteriorated — "covenant-lite" loans are now 90%+ of new issuance, meaning lenders have fewer protections. Default rates in leveraged loans are rising but hidden by PIK (payment-in-kind) and amendment-and-extend strategies that delay recognition. If there is a recession, private credit default rates could spike above 10%, threatening the funds and insurance companies that hold these assets. We monitor via CLO issuance volumes, leveraged loan default rates, and bid-ask spreads in secondary markets — all available via news/RSS analysis.

**110. IPO / Equity Issuance** *(NEW)*
We include this at lower priority because IPO activity is a **proxy for risk appetite and capital formation.** When IPOs are booming (2020-21: 1,035 IPOs), it signals euphoria and excess liquidity. When the IPO window shuts completely (2022: virtually zero tech IPOs), it signals extreme risk aversion and a capital formation drought. The re-opening of the IPO market is a confirming signal that a new risk-on regime has begun.

---

## Gap Analysis: What the Previous 52-Node Graph Missed

Our previous 52-node graph was competent at monitoring US macro fundamentals, rates, and basic equity and commodity markets. But it had **six catastrophic blind spots** that would have left us unable to explain or respond to major historical events:

### Blind Spot 1: Housing (Zero Coverage)
The 2008 GFC was the worst financial crisis in 80 years and it was entirely a housing crisis. Our previous graph had no mortgage rates, no home prices, no housing starts, no CRE indicator. We would have seen credit spreads blowing out and equities crashing but would have had *no path* to explain *why*. Worse, we would not have detected the current slow-moving CRE crisis — office vacancy at 20%+, regional banks stuffed with CRE loans, a structural shift to remote work — because we literally had no factors to monitor it.

### Blind Spot 2: Financial System Plumbing (Zero Coverage)
The September 2019 repo crisis caused overnight rates to spike from 2% to 10%, forcing emergency Fed intervention. SVB's collapse in March 2023 triggered $500B in deposit flight. Both were *plumbing* crises — not about economic fundamentals, but about the mechanics of how banks fund themselves. Without repo rates, bank reserves, financial conditions indices, or lending standards, our system was blind to the entire machinery that connects monetary policy to the real economy.

### Blind Spot 3: China Depth (Minimal Coverage)
We had China PMI — a single lagging indicator. We had no visibility into PBOC policy (the *cause* of China's economic trajectory), China credit impulse (the *leading indicator* of global growth), or China's property sector (*the* structural crisis of the decade). Our system could tell us "China manufacturing is slowing" but could not explain why, predict when it would reverse, or trace the consequences through commodities and EM.

### Blind Spot 4: EM Contagion Chain (Zero Coverage)
We had no EM FX basket, no EM sovereign spreads, no EM equities. This means we could observe that the US dollar was strengthening (DXY up) but could not trace the consequence: EM currencies collapsing → EM debt service costs rising → EM sovereign spreads blowing out → EM equities crashing → capital flight from EM → further DXY strength (a self-reinforcing feedback loop). The 2013 Taper Tantrum, the 2018 EM crisis, and the ongoing EM debt distress were all invisible in our graph.

### Blind Spot 5: Fiscal Policy (Zero Coverage)
We had no US fiscal deficit, no Treasury issuance, no government spending. This meant we attributed the 2023-24 "higher for longer" regime entirely to monetary policy, missing the fiscal dimension: 6%+ GDP deficits funding economic growth (offsetting Fed tightening) and flooding the market with Treasury supply (pushing up term premium). The most important macro debate of 2024 — "fiscal dominance" vs. "monetary control" — was unrepresentable in our graph.

### Blind Spot 6: Real Yields (Zero Coverage)
The real discount rate — the most important price in global finance — was not in our graph. The entire 2022 asset crash (NASDAQ -33%, crypto -75%, ARK -80%) was driven by real yields rising from -1.0% to +2.5%. Without real yields, our system would have seen "stocks are falling" and "rates are rising" as separate phenomena, rather than recognizing them as a single, unified repricing of the discount rate applied to all future cash flows.

---

## Event Coverage Validation

### 2008 Global Financial Crisis
**Chain:** US Home Prices ↓ → Mortgage Defaults ↑ → Bank Lending Standards tighten → HY Credit Spread ↑ → TED Spread ↑ → Commercial Paper freeze → Financial Conditions tighten → S&P 500 ↓↓ → Global contagion via dollar funding stress
**Previously:** **0% coverage** — no housing, no banking, no funding factors
**Now:** **Full coverage** — every link in the chain is monitored

### 2011 European Sovereign Debt Crisis
**Chain:** EU Periphery Spreads (Italy, Greece) ↑ → ECB forced to act → EUR/USD ↓ → EM FX pressure → Global Financial Conditions tighten → Bank CDS spreads ↑ → Contagion risk to US financials
**Previously:** **~10% coverage** — had EUR/USD, nothing else
**Now:** **Full coverage**

### 2013 Taper Tantrum
**Chain:** Fed rate expectations repriced ↑ → US Real Yield ↑ → DXY ↑ → EM FX Basket ↓ → EM Sovereign Spread ↑ → EM Equities ↓ → Capital flight → Further DXY ↑ (feedback loop)
**Previously:** **~30% coverage** — had rate expectations and DXY, no EM chain
**Now:** **Full coverage**

### 2015 China Devaluation Scare
**Chain:** PBOC policy shift → USD/CNY devaluation → China Credit Impulse ↓ → China Equities ↓ → EM Equities ↓ → Copper ↓ → Global growth fears → VIX ↑ → S&P 500 ↓
**Previously:** **~20% coverage** — had USD/CNY and copper, no China depth
**Now:** **Full coverage**

### 2020 COVID Pandemic
**Chain (initial crash):** Supply Chain Pressure ↑ → VIX ↑ → Margin Debt calls → Forced selling → TED Spread ↑ → CP Spread ↑ → Financial Conditions extreme → S&P 500 ↓34%
**Chain (recovery):** US Fiscal Deficit ↑↑ (stimulus) → Consumer Confidence ↑ → PBOC easing → China Credit Impulse ↑ → Commodities ↑ → Global recovery
**Previously:** **~40% coverage** — had market indicators but missed supply chain, funding, and fiscal dimensions
**Now:** **Full coverage**

### 2022 Inflation / Rate Shock
**Chain:** Supply Chain Pressure ↑ + Oil ↑ → US CPI ↑↑ → Fed Funds Rate ↑↑ → Mortgage Rate 3%→7% → Home Prices ↓ → US Real Yield -1%→+2.5% → NASDAQ ↓33% + Bitcoin ↓75% → EM FX Basket ↓
**Previously:** **~50% coverage** — had CPI, rates, equities, but missed housing, real yields, and supply chain as drivers
**Now:** **Full coverage**

### 2022 Russia-Ukraine War
**Chain:** Geopolitical Risk ↑ → Natural Gas ↑10x + Wheat ↑60% → EU HICP ↑10% → ECB forced to hike → EUR/USD ↓ parity → Container Shipping rerouted → Supply Chain Pressure ↑ → Gold ↑ (safe haven)
**Previously:** **~50% coverage** — had commodities and geopolitics, missed EU energy/inflation transmission
**Now:** **Full coverage**

### 2023 SVB Crisis
**Chain:** US Real Yield ↑ → Bank Reserves under pressure + HTM losses on regional bank balance sheets → Regional Banks ↓35% → Deposit flight to Money Market Funds ($500B) → Bank Lending Standards tighten sharply → CRE Stress ↑ → Financial Conditions tighten
**Previously:** **0% coverage** — zero banking, zero funding, zero CRE factors
**Now:** **Full coverage**

### 2024 AI Boom
**Chain:** Semiconductors ↑↑ (NVIDIA) → Tech Sector ↑ → NASDAQ ↑ → Earnings Momentum ↑ → Equity Risk Premium compresses → US Productivity Growth debate → Concentration risk in S&P 500
**Previously:** **~30% coverage** — had NASDAQ and tech, missed semiconductors and ERP
**Now:** **Full coverage**

### 2024 Yen Carry Trade Unwind (August 5th)
**Chain:** BOJ rate hike → USD/JPY reversal → FX Volatility ↑ → Institutional Positioning (extreme JPY shorts) forced to cover → Japan equities ↓12% → VIX ↑65 → S&P 500 ↓3% → EM FX Basket ↓
**Previously:** **~40% coverage** — had USD/JPY and VIX, missed FX vol as a transmission mechanism
**Now:** **Full coverage**

### 2025 Tariff Escalation
**Chain:** Trade Policy ↑↑ → Supply Chain Pressure ↑ → Container Shipping ↑ → US CPI ↑ → China Equities ↓ → EM FX Basket ↓ → Copper ↓ → Global Trade Volume ↓
**Previously:** **~40% coverage** — had trade policy and commodities, missed supply chain and EM transmission
**Now:** **Full coverage**

### Crypto Cycles
**Chain:** Bitcoin ↑/↓ → Retail Sentiment ↑/↓ → Margin Debt ↑/↓ → ETF Flows ↑/↓ → Contagion to/from risk assets via correlation regime
**Previously:** **0% coverage** — crypto entirely absent
**Now:** **Full coverage**

---

## Causal Chain Atlas

The following are the **critical transmission mechanisms** — the pathways through which shocks propagate across categories. These are the edges in our graph that, if severed, would leave us unable to explain market moves.

### Chain 1: Monetary Policy → Real Economy
```
Fed Funds Rate → US 2Y Yield → Mortgage Rate → Housing Starts → GDP
                             → Bank Lending Standards → Credit Supply → GDP
                             → Rate Expectations → Financial Conditions → Equity Prices
```
This is the "textbook" transmission mechanism. It takes 12-18 months.

### Chain 2: Inflation → Policy Response → Asset Repricing
```
Supply Chain Pressure / Oil / Wage Growth → CPI → Fed Funds Rate → Real Yield ↑
Real Yield ↑ → NASDAQ ↓ (growth stocks repriced)
            → Bitcoin ↓ (speculative assets repriced)
            → Gold ↓ (opportunity cost rises)
            → EM FX ↓ (dollar strengthens)
            → Home Prices ↓ (mortgage rates rise)
```
This is the 2022 playbook. Everything falls together because they are all "long duration."

### Chain 3: Financial Plumbing Stress
```
Bank Reserves ↓ → Repo/SOFR spike → TED Spread ↑ → CP Spread ↑
                                                   → Money Market Fund stress
                                                   → Bank Lending Standards tighten
                                                   → Financial Conditions tighten
                                                   → VIX ↑ → Equities ↓
```
This is the 2008/2019/2020/2023 playbook. Happens in *days*, not months.

### Chain 4: China → Global Growth → Commodities
```
PBOC Policy → China Credit Impulse → China Property → Iron Ore
                                                    → China PMI → Copper
                                                    → China Equities → EM Equities
                                                    → Global Trade Volume
```
This chain operates on a 6-9 month lead time. China credit impulse today predicts global industrial production 6 months from now.

### Chain 5: Geopolitics → Supply → Inflation
```
Geopolitical Risk → Sanctions / Trade Policy → Container Shipping ↑
                                              → Natural Gas ↑
                                              → Wheat ↑
                                              → Supply Chain Pressure ↑ → CPI ↑
```
Russia-Ukraine, Red Sea disruption, tariff wars all follow this pattern.

### Chain 6: Dollar Wrecking Ball
```
Fed tightening → DXY ↑ → EM FX Basket ↓ → EM Sovereign Spread ↑
                                         → EM Equities ↓
                                         → Commodities ↓ (priced in USD)
                                         → Capital flight from EM → DXY ↑ (feedback loop)
```
The dollar feedback loop is why EM crises are self-reinforcing.

### Chain 7: Fiscal Dominance
```
US Fiscal Deficit ↑ → Treasury Issuance ↑ → Term Premium ↑ → US 10Y Yield ↑
US Debt/GDP ↑ → DXY ? (uncertain — could strengthen on growth or weaken on credibility)
Government Spending ↑ → GDP ↑ (offsetting monetary tightening)
```
This is the new regime (2023-present) — fiscal and monetary policy working in opposite directions.

### Chain 8: Housing Wealth Effect
```
Mortgage Rate → Home Prices → Consumer Confidence → Consumer Spending → GDP
Home Prices → CPI (shelter inflation, 40% of CPI) → Fed Funds Rate
CRE Stress → Regional Banks → Bank Lending Standards → Credit Supply → GDP
```
Housing affects the economy through wealth effects, inflation, and bank solvency simultaneously.

### Chain 9: Volatility Cascade
```
Initial shock → VIX ↑ → Vol-targeting strategies deleverage → Forced equity selling
                      → Margin calls → More forced selling
                      → Option dealer hedging → Amplified moves
                      → Reduced market-making → Liquidity withdrawal → Wider spreads
```
This is why corrections become crashes. Volatility is not just a *symptom* — it is a *cause*.

---

## Causal Edge Matrix

This section documents every directed causal edge in the factor graph — approximately 1,037 edges across 109 source factors. Each edge represents a structural transmission mechanism: a change in the source factor causally influences the target factor through the described channel.

**Reading the tables:**
- **Direction:** `+` = positive/same-direction (source ↑ → target ↑), `−` = negative/inverse (source ↑ → target ↓), `±` = complex/regime-dependent
- **Mechanism:** Brief description of the transmission channel
- Factors marked **(NEW)** are proposed additions not yet in the 52-node graph

---

### Category 1: US Macroeconomic Fundamentals

**Federal Funds Rate** (24 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Mortgage Rate | + | Pass-through via Treasury curve and MBS spread |
| Repo/SOFR Rate | + | Direct floor for overnight secured funding |
| 2Y Treasury Yield | + | Front-end yields track expected policy path |
| 10Y Treasury Yield | + | Long rates rise on tighter policy, dampened by term premium |
| 30Y Treasury Yield | + | Ultra-long rates respond with lag, anchored by growth expectations |
| Real Yield | + | Nominal rate rises faster than breakevens adjust |
| Yield Curve Spread | − | Rate hikes flatten/invert curve (front end rises faster) |
| Housing Starts | − | Higher rates raise mortgage costs, reduce housing demand |
| Home Prices | − | Reduced affordability suppresses buyer demand |
| Consumer Confidence | − | Higher borrowing costs weigh on consumer outlook |
| S&P 500 | − | Higher discount rate compresses equity valuations |
| NASDAQ | − | Growth/tech stocks most sensitive to discount rate changes |
| Russell 2000 | − | Small caps rely on floating-rate debt, higher costs squeeze margins |
| IG Credit Spread | + | Tighter policy increases default risk perception |
| HY Credit Spread | + | Leveraged issuers face higher refinancing costs |
| DXY (Dollar Index) | + | Rate differential attracts foreign capital, strengthens dollar |
| EUR/USD | − | USD strength from rate differential weakens EUR |
| USD/JPY | + | Wider US-Japan rate gap strengthens USD vs JPY |
| EM FX Basket | − | Dollar strength pressures EM currencies |
| EM Sovereign Spread | + | Higher US rates increase EM debt service costs |
| Gold | − | Higher real rates raise opportunity cost of holding gold |
| Bitcoin | − | Risk-free rate competition reduces speculative appetite |
| Financial Conditions | + | Rate hikes tighten overall financial conditions |
| Rate Expectations | + | Current rate anchors forward expectations |

**US CPI Year-over-Year** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Breakeven Inflation | + | Market inflation expectations track realized CPI |
| Real Yield | − | Higher CPI erodes real return at fixed nominal yield |
| Fed Funds Rate | + | Above-target CPI triggers Fed tightening |
| Rate Expectations | + | Hot CPI prints shift expected rate path higher |
| Consumer Confidence | − | Rising prices erode purchasing power and sentiment |
| Wage Growth | + | Workers demand higher wages to offset cost of living |
| Gold | + | Inflation hedge demand rises with CPI |
| 10Y Treasury Yield | + | Higher inflation expectations push nominal yields up |
| PCE Deflator | + | CPI and PCE are co-integrated, CPI leads expectations |

**US GDP Growth** (13 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Manufacturing PMI | + | GDP growth drives industrial activity and new orders |
| Services PMI | + | Broad growth lifts services sector output |
| Unemployment Rate | − | Okun's law: GDP growth reduces unemployment |
| Fiscal Deficit | − | Growth boosts tax revenue, narrowing deficit |
| Housing Starts | + | Economic expansion supports housing demand |
| Consumer Confidence | + | Growth lifts income expectations and sentiment |
| S&P 500 | + | Earnings growth follows economic expansion |
| Financials | + | Loan growth and asset quality improve with GDP |
| Revenue Growth | + | Corporate top-line tracks nominal GDP |
| Earnings Momentum | + | Revenue growth flows through to earnings |
| HY Credit Spread | − | Growth reduces default risk for leveraged issuers |
| EM Equities | + | US growth supports global demand and risk appetite |
| Fed Funds Rate | + | Strong growth gives Fed room to tighten |

**Unemployment Rate** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Consumer Confidence | − | Rising unemployment destroys consumer sentiment |
| Rate Expectations | − | Higher unemployment signals dovish Fed pivot |
| HY Credit Spread | + | Rising unemployment increases default risk |
| Housing Starts | − | Job losses reduce housing demand |
| Wage Growth | − | Slack labor market reduces wage bargaining power |
| GDP Growth | − | Rising unemployment reduces aggregate demand |
| Retail Sentiment | − | Job insecurity reduces risk appetite |
| Fed Funds Rate | − | Fed eases to support employment mandate |
| Fiscal Deficit | + | Automatic stabilizers (unemployment benefits) widen deficit |

**Manufacturing PMI** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Earnings Momentum | + | Manufacturing expansion drives industrial earnings |
| Revenue Growth | + | New orders translate to corporate revenue |
| Supply Chain Pressure | − | High PMI signals smooth supply chains (inverse stress) |
| Baltic Dry Index | + | Manufacturing expansion increases shipping demand |
| Iron Ore | + | Industrial production drives raw material demand |
| Copper | + | Manufacturing activity is copper-intensive |
| GDP Growth | + | PMI is a leading indicator of GDP |
| S&P 500 | + | Expansion signal supports risk assets |

**PCE Deflator** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Fed's preferred inflation gauge pushes yields |
| 2Y Treasury Yield | + | PCE drives near-term Fed rate expectations |
| Breakeven Inflation | + | PCE validates or challenges market inflation expectations |
| Gold | + | Inflation hedge demand tracks PCE |
| Rate Expectations | + | Hot PCE shifts expected Fed path higher |
| Fed Funds Rate | + | PCE above 2% triggers/sustains tightening |

**Consumer Confidence** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | + | Confidence drives 70% of GDP (consumer spending) |
| Revenue Growth | + | Consumer spending flows to corporate top-line |
| Housing Starts | + | Confident consumers commit to large purchases |
| Services PMI | + | Consumer spending is primarily on services |
| Fund Flows | + | Confident consumers increase investment allocations |

**Wage Growth** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Earnings Momentum | − | Higher wages compress profit margins |
| Services PMI | + | Wage growth supports service sector demand |
| Housing Starts | + | Higher incomes improve housing affordability |
| Rate Expectations | + | Wage-price spiral risk shifts Fed expectations hawkish |
| CPI | + | Labor costs pass through to consumer prices |
| Consumer Confidence | + | Rising wages boost consumer outlook |

**Jobless Claims (NEW)** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Unemployment Rate | + | Claims are a high-frequency leading indicator of unemployment |
| Consumer Confidence | − | Rising claims signal labor market deterioration |
| Rate Expectations | − | Spiking claims signal dovish Fed shift |
| GDP Growth | − | Claims proxy for real-time economic weakness |
| Retail Sentiment | − | Layoff fears reduce risk appetite |
| S&P 500 | − | Claims spikes trigger risk-off (Sahm Rule sensitivity) |
| HY Credit Spread | + | Rising claims increase expected default rates |

**Services PMI (NEW)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | + | Services are ~80% of US GDP |
| S&P 500 | + | Services expansion supports broad earnings |
| Earnings Momentum | + | Service sector profitability drives aggregate earnings |
| Unemployment Rate | − | Service sector is the largest employer |
| CPI | + | Services inflation is the stickiest CPI component |
| Revenue Growth | + | Services demand drives corporate top-line |
| Consumer Confidence | + | Service sector health reflects consumer spending |
| Rate Expectations | + | Strong services = persistent inflation pressure |

**Productivity (NEW)** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Wage Growth | − | Productivity gains allow higher wages without inflation |
| CPI | − | Productivity growth is disinflationary |
| Earnings Momentum | + | Output per worker gains boost profit margins |
| GDP Growth | + | Productivity is a fundamental GDP growth driver |
| Tech Sector | + | Tech investment is the primary productivity channel |
| Revenue Growth | + | More output per worker → more revenue per employee |
| Fed Funds Rate | − | Productivity-driven growth is non-inflationary, less hawkish |

**JOLTS Job Openings (NEW)** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Wage Growth | + | High openings/unemployed ratio gives workers bargaining power |
| Unemployment Rate | − | Abundant openings reduce unemployment duration |
| Consumer Confidence | + | Plentiful jobs boost household sentiment |
| Rate Expectations | + | Tight labor market signals persistent inflation |
| Quits Rate → GDP | + | High quits signal worker confidence, economic dynamism |

**Labor Force Participation (NEW)** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Unemployment Rate | − | Higher participation expands labor supply, can mask weakness |
| Wage Growth | − | Larger labor pool reduces wage pressure |
| GDP Growth | + | More workers → higher potential output |
| CPI | − | Labor supply expansion is disinflationary |
| Fed Funds Rate | ± | Complex: higher participation reduces inflation pressure but signals growth |
| Consumer Confidence | + | Rising participation signals economic engagement |

---

### Category 2: Monetary Policy & Central Banks

**Fed Balance Sheet** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Bank Reserves | + | Asset purchases create reserves in banking system |
| Repo/SOFR Rate | − | Excess reserves push down overnight funding rates |
| Financial Conditions | − | Balance sheet expansion eases financial conditions |
| IG Credit Spread | − | QE portfolio rebalancing compresses credit spreads |
| HY Credit Spread | − | Reach-for-yield effect in credit markets |
| Mortgage Rate | − | MBS purchases directly compress mortgage spreads |
| Term Premium | − | Duration removal suppresses term premium |
| 10Y Treasury Yield | − | Direct price pressure from Treasury purchases |
| S&P 500 | + | Liquidity injection supports risk assets |
| Gold | + | Balance sheet expansion raises inflation expectations |
| DXY | − | Dollar weakens on monetary expansion |
| Bitcoin | + | Liquidity expansion fuels speculative assets |

**Rate Expectations (Fed Funds Futures)** (14 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 2Y Treasury Yield | + | Front-end yields directly reflect rate expectations |
| 10Y Treasury Yield | + | Rate path expectations anchor long yields |
| Mortgage Rate | + | Mortgage rates track expected rate path + spread |
| EUR/USD | − | Hawkish Fed expectations strengthen USD, weaken EUR |
| USD/JPY | + | Higher expected US rates widen US-Japan differential |
| DXY | + | Hawkish expectations attract capital to USD |
| S&P 500 | − | Higher expected rates compress equity valuations |
| NASDAQ | − | Growth stocks most sensitive to rate path |
| Financial Conditions | + | Hawkish expectations tighten financial conditions |
| REITs | − | Higher expected rates reduce present value of rental streams |
| Gold | − | Higher expected real rates raise gold's opportunity cost |
| EM Sovereign Spread | + | Expected US rate rises pressure EM debt sustainability |
| EM FX Basket | − | Hawkish Fed expectations cause EM capital outflows |
| Russell 2000 | − | Small caps sensitive to floating-rate debt costs |

**QE Pace** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Bank Reserves | + | Faster QE creates more reserves |
| Repo/SOFR Rate | − | Reserve abundance pushes funding rates to floor |
| 10Y Treasury Yield | − | Treasury purchases suppress yields |
| 30Y Treasury Yield | − | Duration removal across the curve |
| IG Credit Spread | − | Portfolio rebalancing compresses spreads |
| HY Credit Spread | − | Reach-for-yield intensifies with faster QE |
| Term Premium | − | Removing duration supply suppresses term premium |
| S&P 500 | + | Liquidity injection supports asset prices |
| Financial Conditions | − | QE eases financial conditions broadly |
| Gold | + | Inflation expectations rise with monetary expansion |
| Mortgage Rate | − | MBS purchases directly lower mortgage rates |
| DXY | − | Monetary expansion weakens the dollar |

**Global Central Bank Liquidity** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Equities | + | Global liquidity expansion supports EM risk assets |
| EM FX Basket | + | Liquidity flush weakens USD, supports EM currencies |
| HY Credit Spread | − | Global liquidity compresses credit risk premia |
| Bitcoin | + | Excess liquidity flows into speculative assets |
| Copper | + | Liquidity supports commodity speculation and demand |
| Gold | + | Central bank expansion raises debasement fears |
| S&P 500 | + | Global liquidity is a macro tailwind for equities |
| VIX | − | Liquidity abundance suppresses volatility |
| IG Credit Spread | − | Global reach-for-yield compresses IG spreads |
| Financial Conditions | − | Coordinated expansion eases global conditions |
| EM Sovereign Spread | − | Liquidity reduces EM refinancing risk |
| DXY | − | Non-Fed expansion narrows rate differentials |

**ECB Policy Rate (NEW)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EUR/USD | + | Higher ECB rates strengthen euro vs dollar |
| EU HICP | − | Tighter policy suppresses eurozone inflation |
| Europe Equities | − | Higher rates compress European equity valuations |
| EU Periphery Spreads | + | Tighter ECB policy widens peripheral risk premia |
| IG Credit Spread | + | European credit spreads widen on tightening |
| Financial Conditions | + | ECB tightening tightens European financial conditions |
| Global CB Liquidity | ± | ECB QT reduces global liquidity pool |
| DXY | − | Stronger EUR weakens DXY |

**PBOC Policy (NEW)** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| USD/CNY | − | PBOC easing weakens CNY vs USD |
| China PMI | + | Monetary stimulus supports Chinese industrial activity |
| China Credit Impulse | + | PBOC easing expands credit flow |
| China Property | + | Lower rates support property sector financing |
| Copper | + | China stimulus boosts industrial commodity demand |
| Iron Ore | + | Chinese construction and manufacturing demand rises |
| EM Equities | + | China stimulus spills over to EM demand |
| Global CB Liquidity | + | PBOC expansion adds to global liquidity pool |
| EM FX Basket | + | Chinese demand supports EM export economies |
| Global Trade Volume | + | Chinese demand is a major global trade driver |

**Term Premium (NEW)** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Term premium is a direct component of long yields |
| 30Y Treasury Yield | + | Ultra-long bonds most sensitive to term premium |
| Yield Curve Spread | + | Rising term premium steepens the curve |
| Mortgage Rate | + | Mortgage rates include term premium component |
| S&P 500 | − | Higher term premium raises equity discount rate |
| REITs | − | Rate-sensitive REITs suffer from term premium rises |
| MOVE Index | + | Term premium volatility drives rate vol |
| Financial Conditions | + | Rising term premium tightens financial conditions |
| IG Credit Spread | + | Credit spreads widen as risk-free rate rises |
| DXY | + | Higher term premium attracts foreign capital |
| Gold | − | Higher real long-term rates raise gold's opportunity cost |

---

### Category 3: Rates, Credit & Housing

**2-Year Treasury Yield** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Yield Curve Spread | − | Rising 2Y (front end) flattens/inverts curve |
| Mortgage Rate | + | Short-rate expectations anchor mortgage pricing |
| Repo/SOFR Rate | + | Front-end yields and repo rates are tightly linked |
| DXY | + | Higher short rates attract carry trade capital |
| Financials | + | Banks earn more on short-duration assets |
| Gold | − | Higher short-term real rates raise gold's opportunity cost |
| EM Sovereign Spread | + | Rising US short rates tighten EM financing |
| S&P 500 | − | Higher risk-free rate compresses equity valuations |
| NASDAQ | − | Growth stocks sensitive to front-end rate moves |
| IG Credit Spread | + | Rising rates increase corporate refinancing risk |
| Consumer Confidence | − | Higher borrowing costs weigh on sentiment |
| EUR/USD | − | USD strength from rate differential |

**10-Year Treasury Yield** (20 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Mortgage Rate | + | 30Y mortgage rate tracks 10Y yield + MBS spread |
| S&P 500 | − | Equity risk premium compresses as discount rate rises |
| NASDAQ | − | Long-duration growth stocks most rate-sensitive |
| PE Valuations | − | Higher discount rate compresses PE multiples |
| Equity Risk Premium | − | ERP = earnings yield minus 10Y yield |
| Gold | − | Nominal yield rise increases gold's opportunity cost |
| Housing Starts | − | Higher rates crush housing affordability |
| CRE Stress | + | Higher cap rates stress commercial property values |
| REITs | − | REITs priced as yield instruments, compete with Treasuries |
| DXY | + | Higher US yields attract global capital |
| EM Sovereign Spread | + | EM debt repriced relative to US risk-free rate |
| EM FX Basket | − | Yield differential drives capital out of EM |
| Fiscal Deficit | + | Higher debt service costs widen deficit |
| Financials | ± | NIMs improve but bond portfolio losses (SVB dynamic) |
| Home Prices | − | Affordability erosion suppresses home prices |
| 30Y Treasury Yield | + | Long-end yields are correlated across maturity |
| Breakeven Inflation | ± | Nominal yield = real yield + breakeven |
| IG Credit Spread | + | Rising rates increase corporate debt burden |
| Europe Equities | − | Global rate spillover affects European valuations |
| Japan Equities | − | US-Japan rate differential affects carry trades |

**30-Year Treasury Yield** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Mortgage Rate | + | Ultra-long rate anchors 30Y fixed mortgage pricing |
| REITs | − | REITs compete with ultra-long bond yields |
| CRE Stress | + | Higher long rates stress CRE cap rates |
| PE Valuations | − | Long-term discount rate compresses multiples |
| Home Prices | − | Mortgage affordability erodes with ultra-long rates |
| Fiscal Deficit | + | Higher long-term debt service costs |
| Term Premium | + | 30Y yield is most term-premium-sensitive maturity |

**Yield Curve Spread (10Y-2Y)** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Financials | + | Steeper curve improves bank NIMs |
| Regional Banks | + | Regional banks most dependent on curve steepness for NIMs |
| Lending Standards | − | Steeper curve incentivizes lending (higher NIM reward) |
| Russell 2000 | + | Small caps benefit from bank lending expansion |
| GDP Growth | + | Steeper curve signals economic expansion expectations |
| Recession Probability | − | Inversion is the most reliable recession predictor |
| S&P 500 | + | Curve steepening signals growth, supports equities |
| Consumer Confidence | + | Normal curve signals healthy economy |
| HY Credit Spread | − | Curve steepening reduces recession/default expectations |

**IG Credit Spread** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| HY Credit Spread | + | IG widening signals broader credit stress |
| S&P 500 | − | Wider credit spreads signal risk aversion |
| Financials | − | Bank credit portfolios lose value |
| Buybacks | − | Higher borrowing costs reduce buyback financing |
| Financial Conditions | + | Wider spreads tighten financial conditions |
| CDS Spreads | + | Credit stress reprices default insurance |
| CP Spread | + | Commercial paper spreads widen sympathetically |
| Private Credit | + | Stress reprices private lending risk |
| Earnings Momentum | − | Higher corporate funding costs compress margins |
| Revenue Growth | − | Credit tightening reduces economic activity |

**HY Credit Spread** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | − | HY spread is a leading risk appetite indicator |
| Russell 2000 | − | Small caps are quasi-HY credit instruments |
| VIX | + | Credit stress amplifies equity volatility |
| CDS Spreads | + | HY stress reprices default swap markets |
| Financial Conditions | + | Wider HY spreads tighten conditions |
| Lending Standards | + | Banks tighten lending when HY signals stress |
| Earnings Momentum | − | Higher funding costs compress earnings |
| IPO Issuance | − | Credit stress freezes IPO market |
| Private Credit | + | HY stress reprices private credit risk |
| EM Sovereign Spread | + | HY stress signals global risk aversion |
| Regional Banks | − | Leveraged loan portfolios deteriorate |
| Energy Sector | − | Energy is the largest HY sector |

**Real Yield (TIPS)** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Gold | − | Gold is a zero-coupon real asset — competes with real yield |
| S&P 500 | − | Higher real rates raise true discount rate for equities |
| NASDAQ | − | Long-duration tech stocks most sensitive to real rates |
| DXY | + | Higher real yields attract foreign capital |
| PE Valuations | − | Real discount rate compresses multiples |
| Bitcoin | − | Positive real yields reduce appeal of non-yielding assets |
| EM Sovereign Spread | + | Higher US real rates tighten EM financial conditions |
| EM FX Basket | − | Real rate differential drives EM capital outflows |
| REITs | − | Higher real rates compress REIT valuations |
| Equity Risk Premium | − | ERP shrinks as real rates rise |
| Copper | − | Higher real rates suppress commodity speculation |
| Tech Sector | − | Growth stocks' future cash flows discounted more heavily |

**Breakeven Inflation** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Rising breakevens push nominal yields higher |
| Gold | + | Inflation expectations drive gold demand |
| Brent Crude Oil | + | Oil and breakevens are co-integrated |
| Rate Expectations | + | Rising inflation expectations shift Fed path hawkish |
| DXY | − | Higher inflation expectations weaken purchasing power |
| CPI | + | Breakevens reflect and reinforce inflation expectations |
| Consumer Confidence | − | Expected inflation erodes purchasing power outlook |
| Energy Sector | + | Energy assets are inflation beneficiaries |
| Bitcoin | + | Inflation expectations drive crypto inflation-hedge narrative |
| Fed Funds Rate | + | Persistent breakeven rises trigger Fed tightening |

**5Y5Y Forward Inflation** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Fed Funds Rate | + | If 5Y5Y unanchors above 2.5%, Fed forced to respond regardless of employment |
| Rate Expectations | + | Long-run inflation expectations shift the entire rate path |
| 10Y Treasury Yield | + | Long-run inflation component embedded in nominal yields |
| Gold | + | Long-run inflation expectations drive structural gold demand |
| Consumer Confidence | − | Unanchored long-run expectations signal lost credibility |

**EM Sovereign Spread** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Equities | − | Wider spreads signal EM risk, suppress equity valuations |
| EM FX Basket | − | Spread widening triggers EM capital flight |
| Fund Flows | − | Wider EM spreads cause portfolio rebalancing away from EM |
| China Equities | − | China-specific risk repriced in EM stress |
| Copper | − | EM stress reduces commodity demand expectations |
| VIX | + | EM contagion risk raises global volatility |
| HY Credit Spread | + | EM stress is a global credit risk transmission channel |

**Housing Starts** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | + | Residential construction is a GDP component |
| Home Prices | + | More supply initially signals demand; shortage → price up |
| Copper | + | Residential construction is copper-intensive |
| Unemployment Rate | − | Construction employs millions directly |
| Iron Ore | + | Steel demand for construction |
| Consumer Confidence | + | Housing activity signals economic health |
| Lumber/Timber | + | Direct input demand |

**Home Prices (Case-Shiller)** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Consumer Confidence | + | Wealth effect from homeownership |
| CPI | + | Shelter inflation = 40% of CPI |
| PCE Deflator | + | Shelter component in PCE |
| GDP Growth | + | Wealth effect supports consumer spending |
| REITs | + | Residential REITs track home price trends |
| Housing Starts | + | Rising prices incentivize new construction |
| Financials | + | Mortgage portfolio values increase |
| Regional Banks | + | Mortgage collateral values improve |
| Retail Sentiment | + | Household wealth drives risk appetite |

**Mortgage Rate (30Y Fixed)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Housing Starts | − | Higher mortgage rates kill housing demand |
| Home Prices | − | Affordability erosion suppresses prices |
| Consumer Confidence | − | Monthly payment burden affects sentiment |
| GDP Growth | − | Housing sector contraction drags GDP |
| REITs | − | Residential REITs suffer from housing slowdown |
| Financials | ± | Higher rates boost NIM but reduce origination volume |
| Regional Banks | ± | Same NIM vs. volume tradeoff |
| CRE Stress | + | Rate pass-through to commercial mortgages |

**Commercial Real Estate Stress** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Regional Banks | − | CRE is ~30% of regional bank loan portfolios |
| Financials | − | Large bank CRE exposure via CMBS |
| Lending Standards | + | CRE losses trigger bank deleveraging |
| IG Credit Spread | + | CRE stress reprices corporate credit risk |
| HY Credit Spread | + | CRE-linked HY bonds sell off |
| REITs | − | Direct mark-to-market on property values |
| Financial Conditions | + | CRE stress tightens conditions via bank channel |
| GDP Growth | − | Construction contraction and reduced business investment |
| Private Credit | + | Private CRE lenders face writedowns |
| CDS Spreads | + | Bank CDS widens on CRE exposure |

**Financial Conditions Index (FCI)** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | − | Tighter FCI constrains economic activity |
| S&P 500 | − | Tighter conditions suppress equity prices |
| Russell 2000 | − | Small caps most sensitive to financial conditions |
| HY Credit Spread | + | Tight FCI pushes out credit spreads |
| Housing Starts | − | Tighter conditions reduce mortgage availability |
| Consumer Confidence | − | Credit tightening weighs on sentiment |
| Earnings Momentum | − | Tighter conditions compress corporate earnings |
| IPO Issuance | − | Tight conditions freeze new issuance |
| Buybacks | − | Higher borrowing costs reduce buyback funding |
| Lending Standards | + | Banks respond to tight FCI by tightening further |
| Private Credit | + | FCI tightening reprices private lending |

**Bank Lending Standards** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | − | Tighter lending suppresses investment and consumption |
| Housing Starts | − | Tighter construction and mortgage lending |
| CRE Stress | + | Tighter lending = CRE refinancing risk |
| Russell 2000 | − | Small caps rely on bank lending |
| IG Credit Spread | + | Tighter lending pushes borrowers to bond market |
| HY Credit Spread | + | Credit rationing reprices high-yield risk |
| Unemployment Rate | + | Credit contraction leads to layoffs |
| Consumer Confidence | − | Credit availability affects sentiment |
| Revenue Growth | − | Less credit = less economic activity |
| Private Credit | + | Shadow lending grows when banks retreat |

**Bank Reserves** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Repo/SOFR Rate | − | Abundant reserves suppress overnight funding rates |
| TED Spread | − | Ample reserves reduce interbank stress |
| Financial Conditions | − | Reserve abundance eases conditions |
| Lending Standards | − | Banks with ample reserves lend more freely |
| S&P 500 | + | Reserve abundance is a liquidity tailwind |
| VIX | − | Plentiful reserves suppress systemic risk fears |
| CP Spread | − | Ample reserves ease commercial paper markets |

**Repo/SOFR Rate** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 2Y Treasury Yield | + | Repo rate anchors very short-term yield expectations |
| TED Spread | + | Repo stress widens interbank risk premia |
| CP Spread | + | Repo stress transmits to commercial paper market |
| Financial Conditions | + | Repo rate spikes tighten conditions (Sept 2019 example) |
| Fund Flows | − | Higher funding costs reduce leveraged fund activity |
| Bank Reserves | − | High repo rates signal reserve scarcity |
| Private Credit | + | Funding cost pass-through to leveraged lending |
| IG Credit Spread | + | Repo stress widens investment-grade spreads |

**TED Spread** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Financial Conditions | + | TED spread is a core FCI component |
| IG Credit Spread | + | Interbank stress transmits to corporate credit |
| HY Credit Spread | + | Bank stress amplifies credit risk repricing |
| Lending Standards | + | Banks tighten lending during interbank stress |
| VIX | + | Banking stress raises equity volatility |
| S&P 500 | − | Bank stress is a systemic risk signal |
| Financials | − | Direct indicator of bank sector stress |
| CP Spread | + | Short-term funding stress is interconnected |
| Regional Banks | − | Smaller banks more vulnerable to funding stress |

**Commercial Paper Spread** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Financial Conditions | + | CP stress tightens short-term funding conditions |
| IG Credit Spread | + | CP stress signals broader corporate funding pressure |
| Earnings Momentum | − | Higher funding costs compress margins |
| Revenue Growth | − | Working capital stress constrains business activity |
| S&P 500 | − | Corporate funding stress weighs on equities |
| Fund Flows | − | Higher CP rates reduce leveraged positioning |
| Lending Standards | + | CP stress causes banks to ration credit |

**Private Credit** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| HY Credit Spread | + | Private credit stress reprices public HY risk |
| Lending Standards | + | Private credit losses trigger bank re-evaluation |
| Russell 2000 | − | Small caps rely on private credit for financing |
| Financial Conditions | + | Private credit stress tightens conditions |
| Earnings Momentum | − | Borrower stress reduces earnings quality |
| CDS Spreads | + | Private credit losses increase default expectations |
| Regional Banks | − | Banks with private credit fund exposure lose |
| IPO Issuance | − | Private credit stress freezes exit markets |

**Money Market Fund Flows** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Bank Reserves | − | Deposit flight from banks to MMFs drains bank reserves (SVB: $500B in one week) |
| Lending Standards | + | Deposit outflows force banks to tighten lending |
| Regional Banks | − | MMF competition for deposits is existential for smaller banks |
| Financials | − | Bank disintermediation reduces fee income and lending capacity |
| Repo/SOFR Rate | − | MMF inflows into overnight repo push SOFR down (MMFs are primary repo lenders) |
| Financial Conditions | ± | Outflows from MMFs back into equities ease conditions; inflows to MMFs tighten bank funding |
| S&P 500 | ± | MMF outflows back to equities fuel rallies; MMF inflows signal risk-off |

---

### Category 4: Geopolitics, Fiscal Policy & Supply Chain

**Geopolitical Risk Index** (15 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | − | Risk-off repricing on geopolitical escalation |
| Natural Gas | + | Supply disruption fears (Middle East, Russia) |
| IG Credit Spread | + | Uncertainty premium widens credit spreads |
| HY Credit Spread | + | Risk aversion reprices high-yield debt |
| MOVE Index | + | Geopolitical uncertainty raises rate volatility |
| SKEW | + | Tail risk hedging demand increases |
| EM Sovereign Spread | + | EM perceived as most vulnerable in crises |
| EM Equities | − | Capital flight from EM during geopolitical stress |
| EM FX Basket | − | EM currency depreciation on risk-off |
| Fund Flows | − | Risk-off triggers EM and equity fund outflows |
| FX Volatility | + | Geopolitical uncertainty raises currency vol |
| Uranium | + | Nuclear/energy security premium |
| Retail Sentiment | − | Fear drives retail investor risk aversion |
| Consumer Confidence | − | Geopolitical fears weigh on economic outlook |
| Financial Conditions | + | Geopolitical stress tightens conditions |

**Trade Policy Uncertainty** (18 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Tariffs are a direct pass-through to consumer prices |
| PCE Deflator | + | Import price increases flow through to PCE |
| Supply Chain Pressure | + | Trade barriers disrupt supply chains |
| Copper | − | Trade wars reduce global industrial demand |
| Earnings Momentum | − | Tariff uncertainty depresses capex and margins |
| Revenue Growth | − | Trade barriers reduce global revenue |
| DXY | ± | Complex: tariffs can strengthen USD (demand) or weaken (retaliation) |
| Semiconductors | − | Export controls restrict semis supply chains |
| Tech Sector | − | Tech most exposed to US-China trade restrictions |
| Global Trade Volume | − | Trade barriers directly reduce trade volume |
| Europe Equities | − | Export-dependent Europe hurt by trade wars |
| China Equities | − | China is the primary trade war target |
| EM Equities | − | EM export economies suffer from trade disruption |
| EM FX Basket | − | Trade-dependent EM currencies weaken |
| Russell 2000 | ± | Domestic-focused but hurt by input cost inflation |
| Baltic Dry Index | − | Reduced trade volume depresses shipping rates |
| Iron Ore | − | Trade disruption reduces industrial commodity demand |
| Consumer Confidence | − | Trade uncertainty weighs on economic outlook |

**US Political Risk** (13 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Political instability → fiscal premium on bonds |
| 30Y Treasury Yield | + | Longer-duration bonds most sensitive to political risk |
| IG Credit Spread | + | Uncertainty premium widens corporate spreads |
| HY Credit Spread | + | Risk aversion reprices leveraged credit |
| MOVE Index | + | Policy uncertainty raises rate volatility |
| Consumer Confidence | − | Political turmoil reduces household sentiment |
| Gold | + | Safe-haven demand rises on political risk |
| Treasury Issuance | + | Debt ceiling/fiscal fights affect issuance patterns |
| PE Valuations | − | Uncertainty compresses valuation multiples |
| Financial Conditions | + | Political risk tightens financial conditions |
| REITs | − | Policy uncertainty depresses real estate investment |
| Healthcare | ± | Sector exposed to regulatory/legislative changes |
| Lending Standards | + | Banks tighten in uncertain political environment |

**Sanctions Regime** (13 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Sovereign Spread | + | Sanctions increase EM refinancing risk |
| EM FX Basket | − | Sanctions trigger EM capital flight |
| EM Equities | − | Sanctioned countries' markets sell off, contagion spreads |
| USD/CNY | + | Sanctions strengthen USD as reserve/safe-haven |
| Supply Chain Pressure | + | Sanctions disrupt raw material and component supply |
| Uranium | + | Russia sanctions restrict enriched uranium supply |
| Lithium | + | Sanctions can disrupt critical mineral supply chains |
| Copper | + | Supply disruption from sanctioned producers |
| Global Trade Volume | − | Sanctions directly reduce trade flow |
| Financial Conditions | + | Sanctions tighten conditions for affected regions |
| Bitcoin | + | Sanctions evasion narrative drives crypto demand |
| Europe Equities | − | European firms exposed to sanctioned trade partners |
| Iron Ore | ± | Supply disruption vs. demand destruction |

**Climate Policy** (15 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Energy Sector | ± | Transition costs hurt legacy energy, benefit renewables |
| Brent Crude Oil | − | Demand destruction from decarbonization policies |
| Natural Gas | ± | Transition fuel (bridge) vs. long-term demand destruction |
| Copper | + | Electrification requires massive copper investment |
| Lithium | + | EV battery demand driven by climate mandates |
| Uranium | + | Nuclear renaissance as climate-friendly baseload |
| CPI | + | Carbon taxes and green mandates raise consumer costs |
| IG Credit Spread | + | Stranded asset risk reprices energy credit |
| REITs | − | Building efficiency mandates raise capex |
| Semiconductors | + | Power management chips essential for green tech |
| Housing Starts | ± | Green building mandates raise costs but green subsidies offset |
| Earnings Momentum | ± | Winners (clean tech) vs. losers (fossil fuel) |
| Tech Sector | + | Clean tech investment benefits technology broadly |
| Fiscal Deficit | + | Green subsidies (IRA) widen fiscal deficit |
| Gold | + | Fiscal expansion from climate spending raises inflation fears |

**Tech Regulation** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Tech Sector | − | Regulation caps growth, increases compliance costs |
| NASDAQ | − | Tech-heavy index directly exposed |
| Semiconductors | − | Export controls restrict chips supply chains |
| S&P 500 | − | Tech is 30%+ of S&P 500 by weight |
| PE Valuations | − | Regulatory overhang compresses tech multiples |
| Earnings Momentum | − | Compliance costs and growth caps reduce earnings |
| China Equities | − | US-China tech decoupling restricts market access |
| IPO Issuance | − | Regulatory uncertainty freezes tech IPO pipeline |
| Private Credit | − | Reduced tech venture lending on regulatory risk |
| Buybacks | − | Regulated firms face restrictions on capital return |
| VIX | + | Regulatory uncertainty raises equity volatility |

**Fiscal Deficit** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Treasury Issuance | + | Wider deficit requires more borrowing |
| Debt-to-GDP Ratio | + | Persistent deficits accumulate debt |
| 10Y Treasury Yield | + | Supply effect: more issuance pushes yields up |
| 30Y Treasury Yield | + | Long-term fiscal sustainability premium |
| Term Premium | + | Fiscal risk raises term premium |
| Breakeven Inflation | + | Deficit monetization fears raise inflation expectations |
| DXY | − | Fiscal deterioration undermines dollar credibility |
| Gold | + | Fiscal sustainability concerns drive safe-haven demand |
| Real Yield | + | Risk premium on Treasuries rises |
| IG Credit Spread | + | Government credit risk reprices corporate spreads |
| GDP Growth | + | Short-term fiscal stimulus supports growth |
| CPI | + | Fiscal expansion can be inflationary |

**Debt-to-GDP Ratio** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Term Premium | + | Debt sustainability concerns raise risk premium |
| 10Y Treasury Yield | + | Sovereign credit risk premium in yields |
| 30Y Treasury Yield | + | Longest-duration bonds most sensitive to fiscal risk |
| DXY | − | Credibility erosion weakens reserve currency status |
| Gold | + | Sovereign risk drives gold demand |
| CDS Spreads | + | Sovereign CDS widens on debt trajectory |
| Breakeven Inflation | + | Debt monetization expectations rise |
| Fiscal Deficit | + | Debt service costs create self-reinforcing deficits |
| Financial Conditions | + | Fiscal risk tightens conditions |
| Bitcoin | + | Alternative asset narrative strengthens on sovereign risk |

**Treasury Issuance** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Supply pressure pushes yields up |
| 30Y Treasury Yield | + | Long-end supply is most impactful |
| 2Y Treasury Yield | + | Bill/note issuance affects front-end rates |
| Term Premium | + | Duration supply raises term premium |
| MOVE Index | + | Auction uncertainty raises rate volatility |
| Repo/SOFR Rate | + | Treasury supply absorbs reserves, pressures repo |
| Bank Reserves | − | Reserve drain from Treasury settlement |
| IG Credit Spread | + | Government supply crowds out corporate bonds |
| Financial Conditions | + | Heavy issuance tightens conditions |
| S&P 500 | − | Higher rates from supply compete with equities |
| Fund Flows | − | Treasury supply absorbs investment capital |

**Government Spending** (13 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | + | Direct fiscal multiplier on output |
| Fiscal Deficit | + | Spending widens the deficit |
| CPI | + | Demand-pull inflation from fiscal expansion |
| Unemployment Rate | − | Government hiring and project employment |
| Wage Growth | + | Government wage competition tightens labor market |
| Manufacturing PMI | + | Defense/infrastructure spending supports manufacturing |
| Housing Starts | + | Housing subsidies and infrastructure adjacency |
| Copper | + | Infrastructure spending is copper-intensive |
| Consumer Confidence | + | Fiscal support lifts sentiment |
| Healthcare | + | Healthcare spending is a major government expenditure |
| Rate Expectations | + | Fiscal expansion creates hawkish Fed pressure |
| Semiconductors | + | CHIPS Act and defense spending benefit semis |
| Treasury Issuance | + | Spending requires Treasury financing |

**Supply Chain Pressure Index** (15 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Supply bottlenecks raise consumer goods prices |
| PCE Deflator | + | Supply-side inflation flows through to PCE |
| Manufacturing PMI | − | Supply constraints reduce manufacturing output |
| Earnings Momentum | − | Input cost inflation compresses margins |
| Revenue Growth | ± | Pricing power offsets volume declines |
| Copper | + | Supply bottleneck reprices industrial metals |
| Semiconductors | − | Chip shortages are a key supply chain risk |
| S&P 500 | − | Supply stress weighs on corporate earnings |
| Consumer Confidence | − | Product shortages and price spikes hurt sentiment |
| GDP Growth | − | Supply constraints are a negative supply shock |
| Brent Crude Oil | + | Energy supply disruptions raise oil prices |
| Natural Gas | + | Energy supply chain disruption |
| Baltic Dry Index | + | Shipping bottlenecks raise freight rates |
| China PMI | − | Supply chain stress signals China production disruption |
| Rate Expectations | + | Supply-side inflation complicates Fed easing |

**Baltic Dry Index** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Global Trade Volume | + | Shipping rates proxy for global trade activity |
| Iron Ore | + | Dry bulk shipping = iron ore + coal demand |
| Copper | + | Industrial commodity demand indicator |
| China PMI | + | China is the largest dry bulk importer |
| Manufacturing PMI | + | Shipping activity signals industrial demand |
| Energy Sector | + | Shipping demand indicates energy consumption |
| EM Equities | + | Trade activity benefits EM export economies |
| Wheat | + | Grain shipping costs affect food prices |
| CPI | + | Freight costs pass through to consumer goods |
| Supply Chain Pressure | + | Baltic Dry inversely reflects supply chain ease |

**Container Shipping Rates (Freightos/Drewry)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Container rates are a direct pass-through to goods prices with 2-3 month lag |
| PCE Deflator | + | Import cost pass-through to consumer spending deflator |
| Supply Chain Pressure | + | Container rates are a component of the NY Fed GSCPI |
| Earnings Momentum | − | Higher shipping costs compress margins for import-dependent companies |
| Consumer Confidence | − | Goods price increases from shipping costs are visible to consumers |
| Revenue Growth | ± | Pricing power may offset volume declines for some companies |
| Retail Sentiment | − | Supply delays and price increases frustrate consumers |
| Global Trade Volume | − | Prohibitively high shipping costs reduce trade volumes |

---

### Category 5: Commodities & Currencies

**Brent Crude Oil** (18 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Energy is a direct CPI component |
| PCE Deflator | + | Energy costs flow through to PCE |
| Breakeven Inflation | + | Oil and breakevens are co-integrated |
| Energy Sector | + | Oil price is the primary revenue driver for energy |
| 10Y Treasury Yield | + | Oil-driven inflation expectations push yields |
| Natural Gas | + | Energy substitution and production linkage |
| DXY | − | Higher oil prices weaken dollar (trade balance) |
| Gold | + | Oil-driven inflation boosts gold demand |
| IG Credit Spread | + | Energy credit risk reprices at high oil vol |
| HY Credit Spread | + | Energy is the largest HY sector |
| Consumer Confidence | − | Gas prices are the most visible inflation indicator |
| Fiscal Deficit | + | Energy subsidies and lower tax revenue |
| Baltic Dry Index | + | Oil prices affect shipping fuel costs |
| Supply Chain Pressure | + | Energy costs are a supply chain input |
| EM Sovereign Spread | ± | Exporters benefit, importers suffer |
| Wheat | + | Energy costs affect agricultural production |
| Soybeans | + | Fertilizer and transport costs rise with oil |
| Manufacturing PMI | − | Higher energy costs compress manufacturing margins |

**Gold** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| DXY | − | Gold and dollar are inversely correlated |
| Breakeven Inflation | + | Gold demand signals inflation expectations |
| EM FX Basket | + | Gold strength signals dollar weakness → EM benefit |
| Retail Sentiment | + | Gold rallies excite retail safe-haven interest |
| Bitcoin | + | Alternative asset narrative co-movement |
| Institutional Positioning | ± | COT data shows institutional gold sentiment |
| Mining Equities | + | Gold price drives mining sector profitability |

**Copper** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | + | Copper demand proxy for Chinese industrial activity |
| Manufacturing PMI | + | Dr. Copper: industrial activity barometer |
| Housing Starts | + | Copper demand from residential wiring |
| CPI | + | Copper costs flow through to manufactured goods |
| Iron Ore | + | Industrial commodity complex co-moves |
| Semiconductors | + | Copper is a semiconductor manufacturing input |
| EM Equities | + | Copper exporters (Chile, Peru) benefit |
| Lithium | + | EV metals complex co-movement |
| Supply Chain Pressure | + | Copper bottlenecks signal supply chain stress |
| Baltic Dry Index | + | Copper shipping demand drives dry bulk rates |

**Natural Gas** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Utilities/heating costs are CPI components |
| PCE Deflator | + | Energy cost pass-through |
| Energy Sector | + | Gas is a major revenue source for utilities/E&P |
| EU HICP | + | European inflation heavily gas-dependent |
| Manufacturing PMI | − | High gas prices raise industrial costs |
| Consumer Confidence | − | Heating/utility bills weigh on sentiment |
| Wheat | + | Fertilizer production requires natural gas |
| Soybeans | + | Agricultural input cost linkage |
| Housing Starts | − | Higher utility costs reduce housing attractiveness |
| Uranium | + | Gas price spikes boost nuclear competitiveness |
| Breakeven Inflation | + | Gas-driven inflation expectations |

**Wheat** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Food price inflation component |
| PCE Deflator | + | Food cost pass-through |
| EM Sovereign Spread | + | Food-importing EM nations face balance of payments stress |
| Consumer Confidence | − | Food price spikes are highly visible inflation |
| Geopolitical Risk | + | Food insecurity creates political instability |
| Soybeans | + | Agricultural commodity complex co-movement |
| EM FX Basket | − | Food-importing EM currencies weaken |
| India Growth | − | India is a major food importer; price spikes hurt growth |

**Soybeans** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| CPI | + | Food and feed cost inflation |
| PCE Deflator | + | Food cost pass-through |
| USD/CNY | + | China is the largest soybean importer |
| China PMI | − | Higher input costs compress Chinese margins |
| EM FX Basket | − | Agricultural commodity importers' currencies weaken |
| Wheat | + | Agricultural commodity complex co-movement |
| Global Trade Volume | + | Soybeans are a major global trade commodity |
| Consumer Confidence | − | Food cost increases weigh on sentiment |

**Iron Ore** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | + | Iron ore demand = China steel production proxy |
| China Property | + | Iron ore prices signal construction demand |
| Housing Starts | + | Steel demand from residential construction |
| EM Equities | + | Iron ore exporters (Australia, Brazil) benefit |
| Baltic Dry Index | + | Iron ore is the largest dry bulk commodity |
| Copper | + | Industrial metal complex co-movement |
| CPI | + | Steel costs flow through to construction/auto prices |
| Supply Chain Pressure | + | Iron ore bottlenecks signal industrial stress |
| EM FX Basket | + | AUD, BRL benefit from iron ore strength |

**Lithium** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Semiconductors | + | EV battery management requires power semis |
| Tech Sector | + | EV/battery tech investment benefits tech broadly |
| Copper | + | EV metals complex co-movement |
| China PMI | + | China dominates lithium processing |
| EM Equities | + | Lithium exporters (Chile, Australia) benefit |
| Climate Policy | + | Lithium demand is a direct function of EV mandates |
| Supply Chain Pressure | + | Lithium bottlenecks signal EV supply chain stress |

**Uranium** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Energy Sector | + | Nuclear utilities benefit from uranium price stability |
| Climate Policy | + | Nuclear renaissance narrative strengthens |
| Natural Gas | − | Nuclear baseload substitutes for gas generation |
| EM Sovereign Spread | ± | Uranium exporters (Kazakhstan, Niger) gain/lose |
| Geopolitical Risk | + | Nuclear fuel supply chain is geopolitically sensitive |
| Sanctions | + | Russia enrichment sanctions tighten supply |

**Silver** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Gold | + | Silver tracks gold as precious metal; silver/gold ratio is a risk appetite signal |
| CPI | + | Industrial demand component (solar panels, electronics) links to economic activity |
| Semiconductors | + | Silver is used in semiconductor manufacturing and solar cells |
| Retail Sentiment | + | Silver squeeze events (2021) and retail precious metals interest |
| EM Equities | + | Silver mining concentrated in Mexico, Peru — producer country benefit |

**US Dollar Index (DXY)** (18 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EUR/USD | − | DXY and EUR/USD are inversely related (EUR is 57% of DXY) |
| USD/JPY | + | DXY strength strengthens USD vs JPY |
| USD/CNY | + | DXY strength pressures CNY |
| GBP/USD | − | DXY strength weakens GBP |
| EM FX Basket | − | Dollar strength pressures EM currencies universally |
| Gold | − | Dollar and gold are inversely correlated |
| Brent Crude Oil | − | Oil priced in USD; strong dollar depresses oil |
| Copper | − | Dollar strength depresses commodity prices |
| S&P 500 | ± | Strong dollar hurts multinationals but signals confidence |
| EM Equities | − | Dollar strength triggers EM capital outflows |
| EM Sovereign Spread | + | Dollar strength increases EM debt service costs |
| Earnings Momentum | − | Strong dollar reduces foreign earnings translation |
| Soybeans | − | Dollar-denominated commodities fall |
| Wheat | − | Same commodity pricing mechanism |
| Bitcoin | − | Dollar strength reduces alternative asset demand |
| Iron Ore | − | Dollar strength depresses commodity complex |
| Breakeven Inflation | − | Strong dollar is deflationary for US imports |
| Financial Conditions | + | Strong dollar tightens global financial conditions |

**EUR/USD** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| DXY | − | EUR is the largest DXY component |
| Europe Equities | ± | Weak EUR boosts export earnings but signals weakness |
| EU HICP | − | Weak EUR raises import prices (inflationary) |
| EU Periphery Spreads | + | EUR weakness signals eurozone stress |
| Gold | + | EUR weakness = USD strength headwind, but EUR gold demand rises |
| EM FX Basket | + | EUR moves affect global FX basket dynamics |
| ECB Policy Rate | + | EUR weakness may prompt ECB intervention |

**USD/JPY** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| DXY | + | JPY is 13.6% of DXY |
| Japan Equities | + | Weak yen boosts Japanese export earnings |
| BOJ Policy | − | Excessive yen weakness pressures BOJ to tighten |
| 10Y Treasury Yield | + | Japanese selling of USTs when yen weakens (hedging) |
| VIX | ± | Yen carry unwind triggers vol spikes (Aug 2024) |
| FX Volatility | + | JPY moves amplify global FX vol |
| EM FX Basket | − | Yen carry unwind pressures EM currencies |
| Gold | − | USD/JPY strength = USD strength headwind for gold |

**USD/CNY** (12 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | − | CNY weakness signals capital flight and weak demand |
| China Property | − | CNY depreciation increases foreign debt burden |
| China Credit Impulse | − | Capital outflow pressure constrains credit expansion |
| EM FX Basket | − | CNY weakness triggers competitive devaluation fears |
| China Equities | − | Capital flight depresses equity markets |
| Copper | − | Weak CNY signals weak Chinese demand |
| Iron Ore | − | Same demand signal for construction materials |
| Trade Policy | + | CNY weakness perceived as currency manipulation |
| DXY | + | CNY weakness strengthens broader dollar |
| EM Sovereign Spread | + | CNY depreciation signals EM contagion risk |
| Soybeans | − | Weak CNY reduces Chinese import purchasing power |
| PBOC Policy | + | PBOC intervenes to manage excessive depreciation |

**GBP/USD** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| DXY | − | GBP is a DXY component |
| Europe Equities | + | GBP tracks European risk sentiment broadly |
| EUR/USD | + | European FX complex co-movement |
| US Political Risk | ± | GBP/USD moves on US policy changes |
| FX Volatility | + | Cable is a major vol contributor |

**EM FX Basket** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Equities | + | FX returns are a major component of EM equity returns |
| EM Sovereign Spread | − | EM currency strength eases debt service |
| DXY | − | EM FX strength = broad dollar weakness |
| Copper | + | EM FX strength signals commodity demand health |
| Brent Crude Oil | + | Oil exporter FX tracks crude prices |
| Fund Flows | + | EM currency stability attracts portfolio flows |
| India Growth | + | Rupee stability supports Indian growth |
| China Equities | + | EM FX health signals China demand spillover |
| Global Trade Volume | + | EM FX strength indicates trade health |
| FX Volatility | − | Stable EM FX reduces overall FX vol |

---

### Category 6: Equities, Sectors & Fundamentals

**S&P 500** (18 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| VIX | − | S&P and VIX are inversely correlated |
| Retail Sentiment | + | Rising markets boost retail investor confidence |
| Consumer Confidence | + | Wealth effect from equity portfolio gains |
| PE Valuations | + | Rising prices push up multiples |
| Fund Flows | + | Performance chasing drives inflows |
| IG Credit Spread | − | Rising equities signal risk-on, compress credit spreads |
| HY Credit Spread | − | Same risk-on compression effect |
| CDS Spreads | − | Default risk perception falls with rising equities |
| SKEW | − | Rising markets reduce tail-risk hedging demand |
| Earnings Momentum | + | Stock prices lead and follow earnings |
| Equity Risk Premium | − | Rising prices compress ERP at constant earnings |
| Buybacks | + | Rising stock prices increase buyback activity |
| NASDAQ | + | Broad market moves drive tech-heavy index |
| Russell 2000 | + | Broad risk-on lifts small caps |
| Margin Debt | + | Rising markets increase margin borrowing |
| IPO Issuance | + | Bull markets enable IPO issuance |
| ETF Flows | + | Performance chasing drives passive inflows |
| Financial Conditions | − | Rising equities ease financial conditions |

**NASDAQ Composite** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Tech Sector | + | NASDAQ is the primary tech benchmark |
| Semiconductors | + | Semis are a major NASDAQ component |
| S&P 500 | + | Tech-weighted NASDAQ pulls S&P 500 |
| VIX | − | NASDAQ rallies suppress equity volatility |
| PE Valuations | + | Tech multiples drive aggregate PE |
| Retail Sentiment | + | NASDAQ is the retail investor favorite index |
| Equity Risk Premium | − | NASDAQ rally compresses overall ERP |

**Tech Sector** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| NASDAQ | + | Tech drives NASDAQ returns |
| S&P 500 | + | Tech is 30%+ of S&P by weight |
| Semiconductors | + | Semis are a tech subsector |
| Earnings Momentum | + | Tech earnings drive aggregate earnings growth |
| Revenue Growth | + | Tech revenue growth exceeds other sectors |
| Buybacks | + | Tech generates largest buyback volumes |

**Energy Sector** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Brent Crude Oil | + | Energy equities track oil prices |
| S&P 500 | + | Energy is an S&P 500 sector |
| HY Credit Spread | − | Healthy energy sector compresses HY spreads |
| Earnings Momentum | + | Energy earnings are oil-price-driven |
| Natural Gas | + | Gas producers are in the energy sector |

**Financials Sector** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Financials are an S&P 500 sector |
| Regional Banks | + | Regional banks are a financials subsector |
| IG Credit Spread | − | Healthy financials compress credit spreads |
| Lending Standards | − | Strong banks lend more freely |
| CDS Spreads | − | Strong financials reduce default expectations |
| Private Credit | + | Bank health enables co-lending with private credit |
| Earnings Momentum | + | Financial earnings contribute to aggregate |

**Russell 2000** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Russell risk-on lifts broader market |
| Regional Banks | + | Small-cap banks are Russell components |
| HY Credit Spread | − | Russell strength signals healthy credit conditions |
| Retail Sentiment | + | Small caps are retail favorites |
| Earnings Momentum | + | Small-cap earnings contribute to aggregate |
| IPO Issuance | + | Small-cap rally signals IPO receptivity |

**Healthcare Sector** (3 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Healthcare is a defensive S&P sector |
| Earnings Momentum | + | Defensive earnings contribute to aggregate |
| PE Valuations | + | Healthcare PE contributes to market multiples |

**REITs** (4 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Home Prices | + | Residential REITs track housing market |
| CRE Stress | − | REIT weakness signals CRE stress |
| Housing Starts | + | REIT demand signals housing market health |
| Mortgage Rate | − | REIT returns inversely correlated with mortgage rates |

**Regional Banks** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Lending Standards | + | Regional bank stress tightens credit (SVB dynamic) |
| Financials | + | Regional banks are a financials subsector |
| CRE Stress | + | CRE exposure is regional banks' primary risk |
| Private Credit | + | Regional bank retreat expands private credit market |
| Housing Starts | − | Regional bank stress reduces mortgage lending |
| HY Credit Spread | + | Regional bank stress signals broader credit risk |

**EM Equities** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Sovereign Spread | − | Rising EM equities signal confidence, compress spreads |
| EM FX Basket | + | Equity inflows support EM currencies |
| China Equities | + | China is the largest EM equity market |
| Copper | + | EM equity strength signals commodity demand |
| Fund Flows | + | EM equity performance drives fund allocation |

**Europe Equities** (4 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EUR/USD | + | European equity strength supports EUR |
| S&P 500 | + | Global risk-on lifts all developed markets |
| EU Periphery Spreads | − | European equity strength compresses peripheral risk |
| Earnings Momentum | + | European earnings contribute to global aggregate |

**China Equities** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | + | Equity market signals economic confidence |
| USD/CNY | − | Strong equities attract capital, strengthen CNY |
| Copper | + | Chinese equity strength signals industrial demand |
| Iron Ore | + | Property/construction stocks signal material demand |
| EM Equities | + | China is the EM equity benchmark |
| China Property | + | Property stocks are a major index component |
| China Credit Impulse | + | Equity strength signals credit expansion |
| Brent Crude Oil | + | Chinese demand expectations drive oil |

**Japan Equities (Nikkei)** (4 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| USD/JPY | + | Nikkei and weak yen are correlated |
| BOJ Policy | ± | Equity weakness may prompt BOJ easing |
| Semiconductors | + | Japan semis (Tokyo Electron, etc.) drive global supply |
| S&P 500 | + | Global risk-on correlation |

**Semiconductors** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Tech Sector | + | Semis are the foundation of tech |
| NASDAQ | + | Semis are a major NASDAQ component |
| S&P 500 | + | Mega-cap semis (NVDA, etc.) drive index |
| Revenue Growth | + | Semis revenue signals tech spending cycle |
| Earnings Momentum | + | Semis margins drive tech earnings |
| China Equities | ± | Export controls create winners/losers |
| Copper | + | Chip fabrication requires copper |

**Earnings Momentum** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Earnings are the fundamental equity driver |
| NASDAQ | + | Tech earnings drive NASDAQ |
| Tech Sector | + | Tech earnings are the largest contributor |
| PE Valuations | − | Rising earnings compress PE at constant prices |
| Equity Risk Premium | + | Rising earnings widen ERP at constant yields |
| Buybacks | + | Earnings fund buyback programs |
| HY Credit Spread | − | Strong earnings reduce default risk |
| IG Credit Spread | − | Earnings health compresses credit spreads |
| Revenue Growth | + | Earnings and revenue are co-integrated |
| Russell 2000 | + | Small-cap earnings drive Russell returns |

**PE Valuations (Shiller CAPE)** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Multiple expansion drives index higher |
| NASDAQ | + | Tech multiples drive NASDAQ |
| Equity Risk Premium | − | Higher PE = lower ERP (more expensive) |
| Fund Flows | + | Rising valuations attract momentum-chasing flows |
| Buybacks | − | High valuations reduce buyback cost-effectiveness |
| IPO Issuance | + | High valuations incentivize companies to go public |

**Revenue Growth** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Earnings Momentum | + | Revenue is the top-line driver of earnings |
| S&P 500 | + | Revenue growth supports equity prices |
| PE Valuations | − | Revenue growth validates or stretches multiples |
| Buybacks | + | Revenue growth funds capital return programs |
| GDP Growth | + | Corporate revenue and GDP are co-integrated |
| Wage Growth | + | Revenue growth enables wage increases |

**Equity Risk Premium** (4 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Wider ERP attracts equity allocation |
| Fund Flows | + | Higher ERP signals attractive equity value |
| Buybacks | + | Wide ERP makes buybacks accretive |
| IPO Issuance | + | Healthy ERP supports new equity supply |

**Buybacks** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Buybacks provide direct price support |
| NASDAQ | + | Tech is the largest buyback sector |
| PE Valuations | + | Share reduction inflates per-share earnings |
| Earnings Momentum | + | EPS growth from share count reduction |
| Retail Sentiment | + | Buyback announcements boost retail confidence |

---

### Category 7: Volatility & Risk Pricing

**VIX (CBOE Volatility Index)** (17 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | − | VIX spikes trigger de-risking and forced selling |
| Put/Call Ratio | + | VIX spikes increase put buying |
| IG Credit Spread | + | Equity vol spills over to credit markets |
| HY Credit Spread | + | Vol-driven de-risking widens credit spreads |
| CDS Spreads | + | Default expectations rise with volatility |
| Fund Flows | − | Vol spikes trigger fund redemptions |
| Retail Sentiment | − | Vol spikes destroy retail confidence |
| Margin Debt | − | Margin calls force deleveraging |
| Financial Conditions | + | VIX is a core FCI component |
| SKEW | + | Tail risk awareness rises with VIX |
| FX Volatility | + | Equity vol transmits to FX markets |
| MOVE Index | + | Vol contagion across asset classes |
| PE Valuations | − | Multiple compression during vol events |
| Institutional Positioning | − | Systematic strategies deleverage on vol spikes |
| ETF Flows | − | Vol triggers passive fund redemptions |
| Russell 2000 | − | Small caps most sensitive to vol |
| EM Equities | − | VIX spikes trigger EM risk-off |

**MOVE Index (Bond Volatility)** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | + | Rate vol creates yield risk premium |
| 2Y Treasury Yield | + | Front-end vol affects short-rate expectations |
| VIX | + | Bond vol transmits to equity vol |
| IG Credit Spread | + | Rate vol widens corporate spreads |
| HY Credit Spread | + | Cross-asset vol contagion |
| Mortgage Rate | + | MBS spreads widen during rate vol |
| REITs | − | Rate-sensitive REITs suffer from rate vol |
| Financials | − | Bank bond portfolios face mark-to-market risk |
| Term Premium | + | Rate vol raises term premium |
| FX Volatility | + | Rate vol transmits to currency markets |
| Treasury Issuance | − | High MOVE makes auctions more uncertain |

**Put/Call Ratio** (5 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | ± | Extreme high put/call is contrarian bullish (capitulation); extreme low is contrarian bearish (complacency) |
| VIX | + | High put buying = high implied vol demand = VIX support |
| Retail Sentiment | − | Rising put/call signals retail fear and hedging activity |
| SKEW | + | Elevated put demand shifts the vol skew — puts become relatively expensive |
| Fund Flows | − | High put/call ratio signals defensive positioning, reduces equity inflows |

**SKEW Index** (4 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| VIX | + | Rising SKEW signals tail risk awareness → vol repricing |
| Put/Call Ratio | + | SKEW rise increases OTM put demand |
| Gold | + | Tail risk hedging drives gold demand |
| Institutional Positioning | − | Rising SKEW signals institutional de-risking |

**CDS Spreads (IG CDX)** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| HY Credit Spread | + | IG CDS widening signals broader credit stress |
| IG Credit Spread | + | CDS and cash credit spreads are co-integrated |
| VIX | + | Credit stress amplifies equity volatility |
| S&P 500 | − | CDS widening is a risk-off signal |
| Financials | − | Bank CDS directly measures financial stress |
| Financial Conditions | + | CDS widening tightens conditions |
| Lending Standards | + | Credit stress triggers bank deleveraging |
| Private Credit | + | CDS repricing affects private credit valuation |
| IPO Issuance | − | Credit stress freezes new equity supply |
| EM Sovereign Spread | + | Credit stress contagion hits EM |
| Russell 2000 | − | Small caps most vulnerable to credit stress |

**FX Volatility** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Equities | − | FX vol triggers EM capital flight |
| EM FX Basket | − | FX vol amplifies EM currency depreciation |
| EM Sovereign Spread | + | FX instability widens EM spreads |
| Global Trade Volume | − | FX uncertainty reduces trade activity |
| VIX | + | FX vol transmits to equity volatility |
| Gold | + | Currency instability drives gold demand |
| DXY | ± | FX vol creates dollar safe-haven demand or uncertainty |
| Japan Equities | − | Yen vol disrupts export earnings forecasts |
| Europe Equities | − | EUR vol disrupts European export competitiveness |

---

### Category 8: International Macro

**China PMI (Caixin Manufacturing)** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Iron Ore | + | China manufacturing drives iron ore demand |
| USD/CNY | − | Strong PMI attracts capital, strengthens CNY |
| EM Equities | + | Chinese growth supports EM demand chain |
| China Equities | + | Manufacturing health drives equity performance |
| Baltic Dry Index | + | Chinese imports drive dry bulk shipping |
| Global Trade Volume | + | China is the world's largest trading nation |
| Natural Gas | + | Industrial expansion increases energy demand |
| Supply Chain Pressure | − | Healthy China PMI = smooth supply chains |
| EM FX Basket | + | Chinese demand supports EM export currencies |

**EU HICP (Eurozone Inflation)** (6 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| ECB Policy Rate | + | HICP above target triggers ECB tightening |
| EU Periphery Spreads | + | Tighter ECB policy widens peripheral spreads |
| Europe Equities | − | Higher inflation → tighter ECB → lower valuations |
| Breakeven Inflation | + | European inflation affects global inflation expectations |
| Natural Gas | + | Gas prices drive EU energy inflation |
| Gold | + | European inflation drives global gold demand |

**BOJ Policy** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Japan Equities | ± | BOJ easing supports equities; tightening risks Nikkei |
| Global CB Liquidity | + | BOJ is a major contributor to global liquidity |
| 30Y Treasury Yield | + | BOJ policy shift (YCC exit) affects global long rates |
| FX Volatility | + | BOJ surprises are major FX vol events (Oct 2022, Aug 2024) |
| EM FX Basket | − | BOJ tightening triggers yen carry unwind → EM pressure |
| MOVE Index | + | BOJ policy shifts create global rate vol |
| Europe Equities | − | Yen carry unwind hits global equities |

**China Credit Impulse** (11 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | + | Credit expansion directly supports economic activity |
| China Property | + | Credit flows into property development |
| Copper | + | Credit-funded construction drives copper demand |
| Iron Ore | + | Same construction channel |
| USD/CNY | − | Credit expansion signals domestic demand, strengthens CNY |
| EM Equities | + | Chinese credit expansion supports EM demand |
| China Equities | + | Credit flow supports domestic markets |
| Global Trade Volume | + | Chinese credit expansion boosts import demand |
| Brent Crude Oil | + | Credit-driven demand increases energy consumption |
| Baltic Dry Index | + | Import demand drives shipping rates |
| PBOC Policy | − | Rapid credit expansion may trigger PBOC tightening |

**China Property Market** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| China PMI | + | Property is ~30% of Chinese GDP |
| Iron Ore | + | Property construction drives steel/iron ore demand |
| Copper | + | Wiring and plumbing in construction |
| China Equities | + | Property stocks are a major index component |
| HY Credit Spread | + | China property HY bonds (Evergrande) repriced global HY |
| Consumer Confidence | + | Property wealth effect in Chinese households |
| EM Sovereign Spread | + | China property stress signals EM contagion |
| USD/CNY | − | Property strength attracts capital, supports CNY |
| Gold | + | Property stress drives Chinese safe-haven demand |

**EU Periphery Spreads (BTP-Bund)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EUR/USD | − | Peripheral stress weakens EUR |
| Europe Equities | − | Peripheral risk depresses European equity valuations |
| IG Credit Spread | + | European sovereign stress reprices corporate credit |
| Financials | − | European banks hold peripheral sovereign debt |
| EM Sovereign Spread | + | Contagion from developed market stress to EM |
| VIX | + | European sovereign stress raises global vol |
| Gold | + | Sovereign stress drives safe-haven demand |
| ECB Policy Rate | − | Peripheral stress pressures ECB to ease/support |

**Global Trade Volume** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| GDP Growth | + | Trade is a direct GDP component |
| China PMI | + | China is the world's factory |
| Baltic Dry Index | + | Trade volume drives shipping demand |
| Copper | + | Industrial trade drives commodity demand |
| Brent Crude Oil | + | Trade activity consumes energy |
| EM Equities | + | Trade growth benefits export-driven EM |
| Supply Chain Pressure | − | Trade growth = smoothly functioning supply chains |
| EM FX Basket | + | Trade flows support EM currencies |
| Revenue Growth | + | Global trade supports multinational revenue |
| India Growth | + | India benefits from global trade expansion |

**India Growth Rate** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| EM Equities | + | India is a top-3 EM equity market |
| EM FX Basket | + | Rupee performance affects EM FX basket |
| Brent Crude Oil | + | India is a major oil consumer |
| GDP Growth | + | India contributes ~3.5% of global GDP |
| Gold | + | India is the world's largest gold consumer |
| Global Trade Volume | + | India's trade integration is accelerating |
| Tech Sector | + | Indian IT services sector drives global tech |

---

### Category 9: Flows, Sentiment & Positioning

**Retail Sentiment (AAII Survey)** (9 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | ± | Contrarian indicator at extremes; pro-cyclical at moderate levels |
| NASDAQ | + | Retail flows concentrate in tech/growth |
| Russell 2000 | + | Retail favorites cluster in small caps |
| VIX | − | Bullish retail sentiment suppresses vol |
| Bitcoin | + | Retail enthusiasm drives crypto speculation |
| ETF Flows | + | Retail sentiment drives passive fund inflows |
| IPO Issuance | + | Retail appetite enables IPOs |
| Margin Debt | + | Bullish retail increases margin borrowing |
| Put/Call Ratio | − | Bullish retail reduces put buying |

**Fund Flows (ICI Weekly)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| NASDAQ | + | Tech fund inflows drive NASDAQ |
| IG Credit Spread | − | Bond fund inflows compress credit spreads |
| HY Credit Spread | − | HY fund inflows compress spreads |
| EM Equities | + | EM fund flows drive EM equity performance |
| DXY | ± | Flows into/out of US assets affect dollar |
| Russell 2000 | + | Small-cap fund flows drive Russell |
| PE Valuations | + | Inflows push up multiples |
| ETF Flows | + | Fund flows and ETF flows are co-integrated |

**Institutional Positioning (CFTC COT)** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| 10Y Treasury Yield | ± | Net spec positioning signals yield direction |
| Brent Crude Oil | + | Managed money positioning drives oil price |
| Gold | + | Institutional gold positioning drives prices |
| DXY | + | Net USD positioning affects dollar direction |
| Copper | + | Managed money positioning signals demand |
| SKEW | + | Institutional hedging shows up in SKEW |
| NASDAQ | + | Institutional equity positioning drives tech |

**Margin Debt (FINRA)** (8 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Margin expansion amplifies equity rallies |
| VIX | − | Rising margin debt = complacency → vol suppression |
| Russell 2000 | + | Levered speculation flows to small caps |
| NASDAQ | + | Margin-fueled tech speculation |
| Financial Conditions | − | Rising margin debt = loosening conditions |
| HY Credit Spread | − | Risk-on margin expansion compresses spreads |
| Bitcoin | + | Leveraged speculation spills into crypto |
| SKEW | − | Rising margin debt = reduced tail hedging |

**ETF Flows** (10 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | Passive inflows provide index price support |
| NASDAQ | + | QQQ/tech ETF flows drive NASDAQ |
| IG Credit Spread | − | LQD/IG ETF inflows compress spreads |
| HY Credit Spread | − | HYG/JNK inflows compress HY spreads |
| Gold | + | GLD ETF flows drive gold price |
| EM Equities | + | EEM/VWO flows drive EM equity performance |
| Russell 2000 | + | IWM flows drive Russell 2000 |
| Financials | + | XLF flows drive financial sector |
| Tech Sector | + | XLK/VGT flows drive tech sector |
| Brent Crude Oil | + | USO/energy ETF flows affect oil price |

**IPO Issuance** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| S&P 500 | + | IPO activity signals market health |
| NASDAQ | + | Tech IPOs drive NASDAQ sentiment |
| VIX | − | Active IPO market signals low volatility regime |
| PE Valuations | + | New issuance at high multiples validates valuations |
| Private Credit | − | IPO exits reduce private credit pressure |
| Equity Risk Premium | − | IPO supply increases equity supply → compresses ERP |
| Russell 2000 | + | New listings enter small-cap indices |

**Bitcoin** (7 edges)

| Target | Dir | Mechanism |
|--------|-----|-----------|
| Retail Sentiment | + | Bitcoin rallies amplify risk-on retail enthusiasm |
| NASDAQ | + | Crypto and tech are correlated risk assets |
| Gold | ± | Competing safe-haven/inflation-hedge narratives |
| VIX | − | Bitcoin rallies signal risk-on, suppress vol |
| DXY | − | Bitcoin strength = alternative asset demand vs. USD |
| Margin Debt | + | Crypto leverage amplifies overall margin debt |
| ETF Flows | + | Bitcoin ETF flows (IBIT, etc.) drive crypto prices |

---

*Note: ~1,067 edges across 114 source factors. Some edges appear in both directions (e.g., S&P 500 → VIX and VIX → S&P 500) because the causal relationship flows both ways through different mechanisms. Edge counts include both novel edges proposed by domain-expert agents and edges implicit in existing graph topology. Factors marked (NEW) are proposed additions not yet in the 52-node production graph.*

---

## Expert Review & Upgrade Plan

Three independent domain-expert review teams — (1) Global Macro Research (rates, monetary policy, fiscal, plumbing), (2) Cross-Asset Strategy (equities, vol, commodities, currencies, flows), and (3) Geopolitical Risk & Emerging Markets (geopolitics, EM, housing, supply chain) — conducted a comprehensive audit of all 110 factors and ~1,037 edges. What follows is the consolidated finding.

### Executive Assessment

**Overall Grade:**

| Domain | Grade | Comment |
|--------|-------|---------|
| Factor Selection | B− | 80% right. Critical gaps in plumbing, EM granularity, and several redundancies |
| Edge Specification | C+ | ~55% correct. ~15 edges reversed, ~13 wrong signs, ~14 spurious |
| Plumbing / Funding Stress | D | Missing swap spreads, cross-currency basis, FRA-OIS. Would not have flagged March 2020, Sept 2019 repo, SVB, or UK LDI |
| EM Coverage | D+ | Monolithic "EM Equities" and "EM FX Basket" collapse 40+ countries with 0.4-0.6 inter-regional correlation into single nodes |
| Regime Sensitivity | D | Static +/− signs on edges that are violently regime-dependent. Will be wrong at every regime transition — exactly when the system matters most |

**Three systemic problems that must be fixed before trusting scenario propagation:**

1. **Static edge signs on regime-dependent relationships.** FFR→S&P is marked (−) but is (+) for the first 12-18 months of every hiking cycle with strong growth. The graph will generate false signals at every regime transition.
2. **Causal direction errors.** ~15 edges run backwards — copper doesn't cause PMI, gold doesn't cause breakevens, stock prices don't cause earnings. These produce incorrect cascade directions.
3. **Missing plumbing indicators.** No swap spreads, cross-currency basis, or modern funding stress metrics. The system is blind to the exact conditions that produce the most violent market dislocations.

---

### Factor Audit — Verdicts on All 110 Factors

#### Category 1: US Macroeconomic Fundamentals (14 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 1 | Federal Funds Rate | **Essential** | The single most important price in the global financial system |
| 2 | US CPI | **Essential** | Primary inflation gauge, drives Fed reaction function |
| 3 | US GDP Growth | **Essential (lagging)** | Matters for regime identification but terrible real-time signal. Weight accordingly |
| 4 | Unemployment Rate | **Essential** | Rate of change matters more than level. Sahm Rule trigger |
| 5 | Manufacturing PMI | **Essential** | Best leading indicator; 50 threshold is a genuine regime boundary |
| 6 | PCE Deflator | **MERGE with CPI** | Same phenomenon, different weights. CPI→PCE is an identity, not a causal edge |
| 7 | Consumer Confidence | **Keep, downweight** | Near-zero predictive power for actual consumption. Sentiment echo |
| 8 | Wage Growth | **Essential** | Wage-price spiral is the central bank's nightmare scenario |
| 9 | Jobless Claims | **Essential** | Highest-frequency labor signal. Leads NBER recession calls by 3-6 months |
| 10 | Services PMI | **Essential** | 80% of GDP — arguably more important than Manufacturing PMI |
| 11 | Productivity | **Downweight** | Quarterly, heavily revised, rarely moves markets. Replace with Unit Labor Costs |
| 12 | JOLTS | **Keep** | 2-month lag limits utility, but Beveridge Curve was Fed's 2022-23 analytical framework |
| 13 | Participation Rate | **Keep** | Explains why the unemployment rate lies (post-COVID missing workers) |
| 14 | Fiscal Deficit | **Essential** | THE macro story of 2024-2026. Fiscal dominance vs. monetary control |

#### Category 2: Monetary Policy (7 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 15 | Fed Balance Sheet | **Essential** | QT is the dominant liquidity story of 2023-26 |
| 16 | Rate Expectations | **Essential** | Markets move on expectations, not actuals |
| 17 | QE/QT Pace | **MERGE with Fed Balance Sheet** | QE pace is the flow derivative of balance sheet stock. Redundant |
| 18 | Global CB Liquidity | **Essential** | The "global liquidity tide" — when all four CBs expand, risk assets have tailwind |
| 19 | ECB Rate | **Essential** | Rate differential drives EUR/USD ($7.5T daily volume) |
| 20 | PBOC Policy | **Essential** | The lever behind China's growth cycle |
| 21 | Term Premium | **Essential** | 2023 bond selloff was 100% term premium, not rate expectations |

#### Category 3: Geopolitics (6 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 22 | Geopolitical Risk Index | **Essential** | Lagging newspaper-based measure, but no better systematic alternative exists |
| 23 | Trade Policy | **Essential** | Distinct transmission from GPR — cost-push, supply chain, sector targeting |
| 24 | US Political Risk | **Essential** | Debt ceiling, regulatory pivots, election uncertainty are first-order drivers |
| 25 | Sanctions | **Essential** | Post-2022 sanctions architecture is a new permanent transmission channel |
| 26 | Climate Policy | **Keep** | Misclassified as "geopolitics" — really regulatory/fiscal |
| 27 | Tech Regulation | **Keep** | Misclassified as "geopolitics" — really regulatory |

#### Category 4: Rates & Credit (10 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 28-30 | 2Y, 10Y, 30Y Yields | **Essential** | Three curve points capture different forces (policy, benchmark, fiscal) |
| 31 | Yield Curve Spread | **Essential** | Most reliable recession predictor in existence |
| 32-33 | IG, HY Credit Spreads | **Essential** | HY is the best real-time risk appetite indicator in finance |
| 34 | Real Yield (TIPS) | **Essential** | "The most important price in global finance" — and the graph has few edges from it |
| 35 | Breakeven Inflation | **Essential** | When expectations unanchor, the entire regime changes |
| 36 | 5Y5Y Forward | **Keep** | Fed's own preferred measure of long-run inflation anchoring |
| 37 | EM Sovereign Spread | **Essential** | Only 7 edges — needs significant expansion |

#### Category 5: Volatility (6 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 38 | VIX | **Essential** | Anchor node for the vol cluster |
| 39 | MOVE Index | **Essential** | Bond vol is independent of equity vol in many regimes |
| 40 | Put/Call Ratio | **MERGE into VIX** | 90% explained by VIX level. Not independent |
| 41 | SKEW | **Keep** | Captures tail asymmetry VIX doesn't (low VIX + high SKEW = hidden crash risk) |
| 42 | CDS Spreads | **Essential** | Credit vol, distinct from equity and rates vol |
| 43 | FX Volatility | **Keep** | Genuinely independent — currency vol leads equity vol in EM crises |

#### Category 6: Commodities (10 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 44 | Brent Crude Oil | **Essential** | Single most important commodity |
| 45 | Gold | **Essential** | But critically under-connected — only 7 edges for a $13T+ asset class |
| 46 | Copper | **Essential** | But most outgoing edges are backwards (reflects demand, doesn't cause it) |
| 47 | Natural Gas | **Keep** | Clarify benchmark: Henry Hub vs. TTF are different markets |
| 48 | Silver | **REMOVE** | Redundant with Gold (0.85+ correlation). Industrial signal captured by Copper |
| 49 | Wheat | **Keep** | Food security / geopolitical scenarios |
| 50 | Soybeans | **MERGE with Wheat** | Identical driver set → "Agricultural Commodities" |
| 51 | Iron Ore | **Essential** | Highest-fidelity China construction indicator |
| 52 | Lithium | **REMOVE** | $25B market too small for standalone macro factor |
| 53 | Uranium | **REMOVE** | Tiny market, idiosyncratic supply dynamics |

#### Category 7: Equities (14 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 54 | S&P 500 | **Essential** | Benchmark US index |
| 55 | NASDAQ | **Essential** | Growth/tech proxy |
| 56 | Tech Sector | **MERGE with NASDAQ** | 90% overlap. Double-fires on AI/semis shocks |
| 57 | Energy Sector | **Essential** | Inflation hedge, distinct HY credit linkage |
| 58 | Financials | **Essential** | Monetary policy transmission mechanism |
| 59 | Russell 2000 | **Essential** | Health check for the real US economy |
| 60 | Healthcare | **Downweight** | Only 3 edges. Essentially decorative at current wiring |
| 61 | REITs | **Keep** | Only liquid real-time CRE proxy |
| 62 | Regional Banks | **MERGE into Financials** | Sub-sector noise 95% of the time. Handle SVB-type via scenario shock |
| 63 | EM Equities | **Essential but monolithic** | Needs regional split (Asia/LatAm/CEEMEA have 0.4-0.6 correlation) |
| 64 | Europe Equities | **Keep, under-wired** | Only 4 edges. Missing China demand exposure, ECB policy |
| 65 | China Equities | **Essential** | Moves independently of global factors |
| 66 | Japan Equities | **Keep, under-wired** | Only 4 edges. Missing the mechanical USD/JPY→Nikkei relationship |
| 67 | Semiconductors | **Essential** | Most strategically important industry today |

#### Category 8: Equity Fundamentals (5 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 67 | Earnings Momentum | **Essential** | The fundamental equity driver |
| 68 | PE Valuations | **Keep** | State variable / vulnerability indicator, not a causal driver |
| 69 | Revenue Growth | **MERGE with Earnings** | 0.7+ correlation. False precision |
| 70 | Equity Risk Premium | **Essential** | Underappreciated — key rates↔equities transmission |
| 71 | Buybacks | **Keep** | $1T/yr demand source. Consider reclassifying to Flows |

#### Category 9: Currencies (7 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 72 | DXY | **Essential** | The single most important currency indicator |
| 73 | EUR/USD | **Essential** | Near-tautological with DXY (57.6% weight) — careful of double-firing |
| 74 | USD/JPY | **Essential** | Carry trade systemic risk |
| 75 | USD/CNY | **Essential** | PBOC management = policy signal |
| 76 | GBP/USD | **Replace with AUD/USD** | UK not a significant global macro driver. AUD is the best liquid China/commodity proxy |
| 77 | EM FX Basket | **Essential but monolithic** | Needs regional split |
| 78 | Bitcoin | **Keep as sentiment indicator** | Reclassify from "currency." Almost all outgoing edges should be reversed to incoming |

#### Category 10: Flows & Sentiment (6 Factors)

| # | Factor | Verdict | Rationale |
|---|--------|---------|-----------|
| 79 | Retail Sentiment | **Keep** | But most outgoing edges are backwards — prices drive sentiment |
| 80 | Fund Flows | **Keep** | Clarify: mutual fund vs. hedge fund flows have different dynamics |
| 81 | Institutional Positioning | **Essential** | Only factor in this block with genuine predictive/causal power |
| 82 | Margin Debt | **Keep** | State variable that becomes causal at crisis thresholds (non-linear) |
| 83 | ETF Flows | **MERGE with Fund Flows** | Subset |
| — | IPO Issuance | **REMOVE** | Output not input. Market conditions cause IPOs, not reverse |

#### Categories 11-17: Housing, Plumbing, Fiscal, Supply Chain, Global, Private Credit

All factors **Essential**. No redundancy detected. One critical issue:

- **Container Shipping Rates (Factor #108)** — now wired with 8 edges (CPI, PCE, Supply Chain Pressure, Earnings, Confidence, Revenue, Retail Sentiment, Global Trade Volume). Previously orphaned.

---

### Factors to Add

#### Priority 1 — Critical (System Dangerously Incomplete)

| Factor | Category | Justification |
|--------|----------|---------------|
| **Swap Spreads** | Plumbing | Dealer balance sheet constraint indicator. Negative swap spreads (2015, 2024) signal dealers cannot absorb Treasury duration. Would have flagged March 2020 and UK LDI crisis |
| **Cross-Currency Basis** | Plumbing | EUR/USD and JPY/USD basis measures the cost of dollar funding for non-US banks. Blowout = global dollar shortage. Fed swap lines exist to address this. Missed every dollar funding crisis since 2008 |
| **FRA-OIS Spread** | Plumbing | Modern replacement for the obsolete TED Spread (LIBOR is dead). The fastest real-time indicator of interbank funding stress |
| **OPEC+ / Energy Security** | Geopolitics | Production policy decisions and chokepoint risk (Strait of Hormuz, Bab el-Mandeb). Not captured by GPR Index. When MBS cut 1M bpd in 2023, GPR didn't move but oil moved 15% |
| **Retail Sales** | US Macro | The single best monthly indicator of consumer spending (70% of GDP). Moves markets on release day. Control group retail sales is a direct GDP input. Inexcusable omission |
| **Rental Inflation / OER** | Housing | Owners' Equivalent Rent is 25-26% of CPI and 33% of Core CPI. Without it, the Housing→CPI transmission is a black box with no way to model the 12-18 month lag |
| **RRP Facility Balance** | Plumbing/Monetary | The Fed's Reverse Repo Facility is the primary liquidity buffer indicator. Its drawdown from $2.5T to near zero was THE liquidity story of 2024, explaining why risk assets rallied despite QT |

#### Priority 2 — High (Significant Analytical Gap)

| Factor | Category | Justification |
|--------|----------|---------------|
| **Risk Parity / Vol-Targeting Flows** | Flows | $500B+ in strategies that mechanically sell equities when VIX rises. This is the mechanism behind correlated selloffs. Without it, the graph cannot model the most important feedback loop in modern markets |
| **Implied Correlation** | Volatility | VIX=25 with low correlation (stock-specific events) is a completely different state than VIX=25 with high correlation (systemic risk). The graph cannot distinguish these |
| **CTA / Systematic Positioning** | Flows | Trend-following flows are a genuine causal factor. When CTAs are max long and trend breaks, forced selling cascades |
| **Profit Margins** | Fundamentals | The intersection of inflation and equity fundamentals. Margins compress from wage growth, input costs, pricing power loss. Distinct from earnings growth |
| **Money Market Fund Flows** | Plumbing | $6T+ market. SVB crisis caused $500B deposit-to-MMF migration in one week. The flow from deposits to MMFs is bank disintermediation that tightens credit |
| **Bank CDS / Sub Debt Spreads** | Plumbing | SVB, Credit Suisse, First Republic all signaled distress through bank CDS months before failure. Early warning for systemic bank risk |
| **Treasury Auction Metrics** | Fiscal | Bid-to-cover ratios and auction tails directly move the long end. The October 2023 30Y auction tail triggered a 20bp selloff — the market's real-time verdict on fiscal sustainability |
| **Foreign UST Holdings** | Fiscal | China and Japan have been net sellers since 2022. Marginal buyer shifting from price-insensitive central banks to price-sensitive hedge funds changes duration risk |
| **Japan 10Y / JGB Yields** | Intl Macro | If BOJ normalizes, JGB yields are the transmission mechanism for global rate repricing. July 2024 carry unwind proved this |
| **CMBS Spreads** | Housing | The market-priced equivalent of CRE Stress. CRE Stress is the fundamental factor; CMBS Spreads are the market transmission |
| **AUD/USD** | Currencies | The best liquid commodity currency — higher-fidelity China demand proxy than managed CNY. Replace GBP/USD |
| **Unit Labor Costs** | US Macro | Wages × productivity. What actually drives corporate margin pressure and inflation persistence. More useful than either alone. Replace Productivity |

#### Priority 3 — Medium

| Factor | Category | Justification |
|--------|----------|---------------|
| EM Regional Split (Asia / LatAm / CEEMEA) | EM | 3 equity + 3 FX factors replacing 2 monolithic ones. Inter-regional correlation is only 0.4-0.6. Brazil's dynamics ≠ India's ≠ Turkey's |
| Variance Risk Premium | Volatility | The spread between implied and realized vol. Drives vol selling flows, risk parity leverage, short-vol ETF behavior. Required to model Feb 2018 volmageddon |
| India Equities | Equities | 4th largest equity market globally. Distinct drivers from EM aggregate (domestic consumption, BJP policy, remittances) |
| LNG / TTF European Gas | Commodities | Henry Hub ≠ TTF. European gas prices rose 10x in 2022 on Russia disruption; Henry Hub didn't follow. Different market |
| Carbon Credits (EU ETS) | Regulatory | $900B market, >€80/ton. Directly impacts European energy, industrial, and equity sectors. Increasingly a macro factor |

---

### Edge Corrections

#### A. Edges with Reversed Causality (Direction Backwards)

These edges have the arrow pointing the wrong way. The claimed "cause" is actually the "effect."

| # | Current Edge | Correct Direction | Rationale |
|---|-------------|------------------|-----------|
| 1 | Cu → China PMI (+) | **China PMI → Cu (+)** | Copper reflects demand. China's 55% demand share drives copper, not reverse |
| 2 | Cu → Manufacturing PMI (+) | **PMI → Cu (+)** | "Dr. Copper" is a barometer, not a cause. PMI leads copper |
| 3 | Cu → Housing Starts (+) | **Housing Starts → Cu (+)** | Construction drives copper demand (wiring, plumbing), not reverse |
| 4 | Gold → DXY (−) | **DXY → Gold (−)** | Dollar drives gold, not reverse. DXY→Gold already exists — remove Gold→DXY duplicate |
| 5 | Gold → Breakevens (+) | **Breakevens → Gold (+)** | Inflation expectations drive gold demand, not reverse |
| 6 | Oil → DXY (−) | **DXY → Oil (−)** | Dollar denomination effect. DXY→Oil already exists — remove Oil→DXY duplicate |
| 7 | SPX → Earnings (+) | **Earnings → SPX (+)** | Fundamentals drive price. This is the most basic tenet of equity analysis |
| 8 | SPX → Fund Flows (+) | **Flows → SPX (+)** | Contemporaneously, inflows push price. Performance chasing (SPX→Flows) is a lagged secondary effect |
| 9 | GDP → Manufacturing PMI (+) | **PMI → GDP (+)** | PMI is a LEADING indicator of GDP. Has led every US recession since 1960 |
| 10 | GDP → Services PMI (+) | **Services PMI → GDP (+)** | Services PMI leads GDP, not vice versa |
| 11 | Baltic Dry → Iron Ore (+) | **Iron Ore demand → BDI (+)** | BDI is an output indicator reflecting commodity trade, not a causal driver |
| 12 | Baltic Dry → Global Trade (+) | **Global Trade → BDI (+)** | BDI reflects trade volume. It doesn't cause trade |
| 13 | 10Y → Japan Equities (−) | **10Y → Japan Equities (+) or (±)** | Higher US 10Y → USD/JPY rises → yen weakens → Japanese exporters benefit → Nikkei rises. One of the tightest cross-asset correlations |

#### B. Edges with Wrong or Oversimplified Signs

These edges have the correct direction but the wrong +/− sign, or use a static sign where the relationship is violently regime-dependent.

| # | Edge | Current | Correct | Why |
|---|------|---------|---------|-----|
| 1 | FFR → S&P 500 | (−) | **(±)** | FFR hikes in strong growth environments (1994-95, 2016-18) coincide with rising equities. **Most dangerous oversimplification in the graph** |
| 2 | FFR → Gold | (−) | **(±)** | Gold rallied 70% during 2001-03 easing AND 25% during 2022 hiking. Depends on growth-fear vs. inflation-fear regime |
| 3 | FFR → 10Y Yield | (+) | **(±)** | At terminal rate, 10Y can fall as markets price recession risk from overtightening |
| 4 | FFR → 30Y Yield | (+) | **(±)** | Greenspan's "conundrum" — FFR rose 425bp, 30Y barely moved. 30Y driven by term premium, not FFR |
| 5 | FFR → Home Prices | (−) | **(±)** | 2022-23: supply constraints dominated rate effects. Prices barely fell despite 500bp hikes |
| 6 | Housing Starts → Home Prices | (+) | **(−) or (±)** | More starts = more supply = downward price pressure in equilibrium |
| 7 | Climate → Oil | (−) | **(±)** | Long-term demand destruction vs. medium-term supply underinvestment thesis |
| 8 | Oil → IG/HY Spread | (+) | **(±)** | Oil up → energy credits improve (spreads tighten) BUT inflationary → rates up → broader spread widening |
| 9 | VIX → SKEW | (+) | **(±)** | SKEW often falls during VIX spikes as entire vol surface shifts and relative skew compresses |
| 10 | Margin Debt → VIX | (−) | **(±)** | Rising margin = complacency = low VIX normally. But margin CALLS cause VIX spikes. Sign flips at crisis threshold |
| 11 | Sanctions → Iron Ore | (±) | **(+)** | Supply disruption dominates demand destruction. Russia/Australia sanctions restrict supply |
| 12 | Housing Starts → Iron Ore | (+) | **Reduce weight to ~0.1** | US housing uses wood-frame construction, not steel. Iron ore is a China construction indicator |

#### C. Edges to Remove (Spurious, Tautological, or Correlation-Not-Causation)

| # | Edge | Reason for Removal |
|---|------|-------------------|
| 1 | CPI → PCE (+) | Not causal — they measure the same phenomenon with different baskets. Merge the nodes |
| 2 | SPX → PE (+) | Tautological. PE = Price/Earnings. SPX going up IS PE going up. Accounting identity |
| 3 | Cu → Iron Ore (+) | Common factor (China demand), not causal. Wire both to China PMI instead |
| 4 | Cu → Baltic Dry (+) | Common factor (global trade), not causal |
| 5 | Cu → Semiconductors (+) | Common factor (global cycle), not causal. Both respond to industrial activity |
| 6 | Cu → CPI (+) | Negligible pass-through. Copper is a trivial CPI component |
| 7 | Oil → Gold (+) | Common factor (USD, inflation expectations). No direct transmission mechanism |
| 8 | Oil → Natural Gas (+) | Decoupled in 2021-2023. Different markets (global seaborne vs. regional pipeline), different demand drivers |
| 9 | Oil → Baltic Dry (+) | Ambiguous. Oil is a cost to shipping, not a demand driver. Causality muddled |
| 10 | Gold → Bitcoin (+) | No causal mechanism. Competing stores-of-value with no transmission channel |
| 11 | Cu → Lithium (+) | Narrative "green metals" correlation. No physical transmission |
| 12 | GPR → Retail Sentiment (−) | Too weak. Consumers are remarkably resilient to geopolitical shocks (post-9/11, post-Ukraine) |
| 13 | Climate → Gold (+) | Causal path too indirect to be useful |
| 14 | Earnings → Revenue (+) | Near-tautological. They're co-integrated by construction |

#### D. Critical Missing Edges (Must Add)

| # | Edge | Priority | Rationale |
|---|------|----------|-----------|
| 1 | **Real Yield → Gold (−)** | CRITICAL | THE #1 driver of gold — explains ~80% of variance over 20 years. Currently missing |
| 2 | **GPR → Gold (+)** | CRITICAL | Canonical safe haven trade. Its absence is a serious oversight |
| 3 | **GPR → Oil (+)** | CRITICAL | Every major geopolitical crisis since 1973 has moved oil. Glaring omission |
| 4 | **GPR → VIX (+)** | CRITICAL | Standard risk-off transmission |
| 5 | **GPR → DXY (+)** | HIGH | Risk-off dollar bid (except US-specific political crises) |
| 6 | **GPR → Treasury Yields (−)** | HIGH | Flight to quality — THE defining GPR transmission |
| 7 | **Sanctions → Oil (+)** | CRITICAL | Iranian/Russian sanctions = oil supply shock. Single most important sanctions edge |
| 8 | **Sanctions → Natural Gas (+)** | CRITICAL | Russia sanctions restructured the entire European gas market |
| 9 | **Sanctions → Gold (+)** | HIGH | Central bank reserve diversification post-2022 drove gold rally |
| 10 | **China PMI → Copper (+)** | CRITICAL | 55% of global copper demand. The graph is structurally broken without this |
| 11 | **China PMI → Europe Equities (+)** | HIGH | Luxury, autos, industrials have massive China revenue exposure |
| 12 | **VIX → DXY (+)** | HIGH | Risk-off dollar strength. One of the most reliable cross-asset relationships |
| 13 | **VIX → Gold (+)** | HIGH | Safe haven bid during vol spikes |
| 14 | **VIX → Bitcoin (−)** | HIGH | Crypto collapses in vol spikes. Every time |
| 15 | **USD/JPY → Japan Equities (+)** | CRITICAL | One of the tightest mechanical cross-asset correlations globally |
| 16 | **Earnings → S&P 500 (+)** | CRITICAL | If only SPX→Earnings exists, this reversal is the fundamental equity relationship |
| 17 | **FFR → CRE Stress (+)** | HIGH | CRE is floating-rate financed. Rate hikes directly lethal. Caused 2023-24 stress |
| 18 | **FFR → Private Credit (+)** | MEDIUM | Higher bank costs push borrowers to private credit — biggest structural story of 2023-24 |
| 19 | **GDP → 10Y Yield (+)** | HIGH | Growth expectations are a primary driver of long yields. Glaring omission |
| 20 | **CPI → S&P 500 (−)** | HIGH | Hot CPI prints consistently negative for equities. June 2022: −3.6% in 3 days |
| 21 | **CPI → DXY (+)** | MEDIUM | Higher CPI → higher rate expectations → stronger dollar |
| 22 | **Container Rates → CPI (+)** | HIGH | Wire the orphaned Factor #108. Import cost pass-through |
| 23 | **Container Rates → Supply Chain (+)** | HIGH | Wire the orphaned Factor #108 |
| 24 | **Trade Policy → Container Rates (−)** | HIGH | Wire the orphaned Factor #108 |
| 25 | **10Y → Pension/Insurance (+)** | MEDIUM | Higher long rates improve pension funding ratios — massive structural LDI bid |
| 26 | **Home Prices → Mortgage Delinquency (−)** | MEDIUM | Higher prices = more equity = fewer defaults. Critical for MBS/banks |
| 27 | **Mortgage Rate → Refi Activity (−)** | MEDIUM | 50bp move changes refi volume 30-50%. Critical housing transmission |

#### E. Edges That Must Be Bidirectional

These edges currently run in one direction but have economically real causation flowing both ways. For each pair, implement lag differentiation: the faster direction gets higher weight, the slower return-path gets dampening.

| # | Edge Pair | Why Both Directions Are Real |
|---|-----------|------------------------------|
| 1 | **CPI ↔ Wages** | Wage-price spiral. Workers demand raises from CPI (CPI→Wages). Higher wages push up services CPI (Wages→CPI) |
| 2 | **FFR ↔ Rate Expectations** | Current rate anchors expectations (FFR→RateExp). But rate expectations LEAD FFR at turning points — 2Y prices cuts months before the Fed delivers (RateExp→FFR) |
| 3 | **GDP ↔ Consumer Confidence** | Strong GDP boosts confidence (GDP→Conf). But confidence leads spending which IS GDP (Conf→GDP) |
| 4 | **S&P 500 ↔ VIX** | SPX down → VIX up (instantaneous). VIX spike → forced selling → SPX down (1-3 day lag through gamma hedging and vol-targeting) |
| 5 | **S&P 500 ↔ Buybacks** | Rising market makes buybacks procyclical (SPX→Buybacks). Buybacks provide $1T/yr price support (Buybacks→SPX) |
| 6 | **Fund Flows ↔ S&P 500** | Performance chasing drives flows with lag (SPX→Flows). Flows push price contemporaneously (Flows→SPX) |
| 7 | **VIX ↔ Credit Spreads** | Vol regime transmits to credit same-day (VIX→Credit). Credit stress amplifies vol over weeks (Credit→VIX) |
| 8 | **DXY ↔ Commodities** | Dollar denomination drives commodities (DXY→Commodities). Commodity shocks move DXY through trade balance (Commodities→DXY) |
| 9 | **Fiscal Deficit ↔ 10Y Yield** | Deficit → more issuance → higher yields (Deficit→10Y). Higher yields → higher interest expense → higher deficit (10Y→Deficit) |
| 10 | **EM FX ↔ EM Spread** | THE reflexive doom loop. Currency weakness → higher debt service → wider spreads → capital flight → more currency weakness. Self-reinforcing in crises |
| 11 | **Supply Chain ↔ China PMI** | Global disruptions reduce China output (SC→ChinaPMI). China demand creates bottlenecks (ChinaPMI→SC). Both directions operative within last 3 years |

---

### Structural Critique

#### Feedback Loops Requiring Lag Dampening

The graph contains several circular paths that are economically real but computationally dangerous. If the propagation engine treats them as simultaneous, cascades will oscillate or explode.

| Loop | Lag Profile | Risk |
|------|------------|------|
| FFR → 10Y → Housing → GDP → FFR | Days → Months → Quarters → Quarters | Monetary transmission. If BFS treats as simultaneous, it will oscillate |
| CPI → FFR → DXY → Import Prices → CPI | Full loop: 12+ months | Exchange rate / inflation feedback. Decay function must prevent runaway amplification |
| HY Spread → FCI → GDP → HY Spread | In crisis: weeks to months | The financial accelerator. In normal times decay is 30%/hop. **In crisis, actual decay may be 10%/hop** (amplification, not dampening). Consider regime-dependent decay |
| Deficit → Issuance → 10Y → Deficit | Structural, quarters | The "debt doom loop." Self-reinforcing above certain debt/GDP thresholds. This is the structural risk of the next decade |

**Recommendation:** Encode lag information on each edge and implement asynchronous propagation. An edge should not re-fire within its lag period. For known circular pairs, apply a dampening multiplier (e.g., 0.5×) on the return edge.

#### Leading Indicator vs. Causation Confusion

The graph systematically confuses "X predicts Y" with "X causes Y" in several places:

| Confused Edge | Reality |
|--------------|---------|
| GDP → PMI | PMI **leads** GDP. PMI is a leading indicator, GDP is lagging. Reverse |
| GDP → Services PMI | Same — services PMI leads GDP |
| Unemployment → GDP | GDP **leads** unemployment (Okun's Law). Unemployment is a lagging indicator |
| Baltic Dry → Trade/Commodities | BDI **reflects** trade activity, doesn't cause it. Most outbound edges should be inbound |
| Copper → PMI/China PMI | Copper **reflects** industrial demand. PMI causes copper demand |
| VIX → "everything" | VIX is a **measure** of implied vol, not inherently a cause. VIX receives edges from market stress. (Though VIX-driven hedging flows do feed back — model as a weaker return path) |

#### The Biggest Structural Risk: Static Edge Signs

**A system with static +/− signs will be systematically wrong at every regime transition.** These are the exact moments when a macro surveillance system is most needed.

Examples of regime-dependent edges treated as static:

| Edge | Normal Regime | Crisis Regime | Inflation Regime |
|------|--------------|---------------|------------------|
| FFR → S&P 500 | (+) early cycle, rates rise with growth | (−) overtightening causes selloff | (−) Fed hiking to kill inflation |
| 10Y → S&P 500 | (+) rates rising on growth | (−) rates rising on inflation/supply | (−−) rapid rate rise triggers duration selloff |
| FFR → Gold | (−) higher real rates, opportunity cost | (+) crisis hedge demand | (+) stagflation hedge |
| Stock-Bond Correlation | (−) normal negative correlation | (+) both sell off in funding crises | (+) 2022-23 positive correlation due to inflation |
| USD → EM | (−) generally correct | (−−) self-reinforcing in crisis | Could be (+) for commodity exporters in commodity boom |

**Minimum recommendation:** Define three regimes and encode sign/weight per regime:

1. **Growth Regime** (expansion, low/stable inflation): Standard textbook relationships. Rates up = equities up. Bad news is bad news
2. **Inflation Regime** (overheating, rising inflation): Rates up = equities down. CPI drives everything. Stock-bond correlation turns positive
3. **Crisis Regime** (recession fear, financial stress): Correlations spike to ±1. Liquidity is all that matters. Gold and Treasuries rally regardless of rate direction

#### Non-Linear Threshold Effects

Ten edges where linear propagation is structurally wrong. Below threshold, normal weight applies. Above threshold, the relationship becomes 2-3× stronger due to mechanical/forced flows.

| Edge | Threshold | Mechanism |
|------|-----------|-----------|
| VIX → Margin Debt | VIX > 30 | Below 30: margin grows calmly. Above 30: margin calls trigger forced selling cascade |
| VIX → S&P 500 | VIX > 35-40 | Above 35: gamma hedging forces dealers to sell, creating positive feedback loop |
| VIX → Institutional Positioning | VIX > 25 | Risk parity / vol-targeting deleveraging triggers at vol thresholds. Rule-based, not discretionary |
| Margin Debt → S&P 500 | Margin declining >5% MoM | Expansion is slow and positive. Contraction is fast and violent. Most asymmetric edge |
| CDS → Financials | CDS > 150bps | Below 100: noise. 100-150: attention. >150: counterparty risk, deposit flight, bank run dynamics |
| MOVE → Mortgage Rate | MOVE > 120 | MBS hedging convexity kicks in, creating self-reinforcing rate vol (2023 regional bank crisis) |
| EM FX → EM Spread | EM FX index −10% | Gradual weakness: manageable. Sharp depreciation: dollar debt spirals, reserve depletion, IMF territory |
| USD/JPY → VIX | Rapid JPY appreciation >3%/week | Slow yen moves: orderly. Sharp: carry trade unwind → forced selling → vol spike (August 2024) |
| Oil → CPI | Oil ±30% | Small moves pass through gradually. Large spikes/crashes have non-linear consumer confidence effects |
| S&P 500 → Consumer Confidence | SPX −20% | Bear market threshold: negative wealth effect on spending becomes acute |

**Recommendation:** Implement a threshold multiplier on these edges. Below threshold: normal weight. Above threshold: multiply weight by 2-3×.

#### Sign Convention Inconsistency — China Property

The China Property factor has internally contradictory edge signs suggesting confusion about whether Property measures "health" (higher = better) or "stress" (higher = worse):

| Edge | Implies Property = |
|------|-------------------|
| Property → China PMI (+) | Health (better property → better PMI) |
| Property → USD/CNY (−) | Health (better property → stronger CNY → lower USD/CNY) |
| Property → HY Spread (+) | **Stress** (more stress → wider HY spreads) |
| Property → Gold (+) | **Stress** (more stress → safe haven buying) |
| Property → EM Spread (+) | **Stress** (more stress → wider EM spreads) |

**Resolution:** Define Property as **health** (higher = better property market). Then fix:
- Property → HY Spread: change to **(−)** (healthier property → tighter spreads)
- Property → Gold: change to **(−)** (healthier property → less safe haven demand)
- Property → EM Spread: change to **(−)** (healthier property → tighter spreads)

---

### Factor Budget Summary

| Action | Count | Details |
|--------|-------|---------|
| **Merge** | −8 factors | PCE→CPI, QE→BS, Put/Call→VIX, Tech→NASDAQ, Regional Banks→Financials, Revenue→Earnings, ETF→Fund Flows, Soybeans→Wheat |
| **Remove** | −4 factors | Silver, Lithium, Uranium, IPO Issuance |
| **Replace** | 3 swaps | TED→FRA-OIS, GBP→AUD, Productivity→ULC |
| **Add Priority 1** | +7 factors | Swap Spreads, Cross-Currency Basis, FRA-OIS, OPEC+, Retail Sales, OER/Rental Inflation, RRP |
| **Add Priority 2** | +12 factors | Risk Parity, Implied Corr, CTA, Margins, MMF Flows, Bank CDS, Auction Metrics, Foreign UST, JGB, CMBS, AUD, ULC |
| **Add Priority 3** | +8 factors | EM Regional Split (×6), Variance Risk Premium, India Equities, LNG/TTF, Carbon Credits |
| **Conservative path** | ~105 factors | Merges + Removes + P1 Adds only |
| **Full upgrade** | ~125 factors | All changes. More accurate, denser, better wired |

---

### Implementation Roadmap

#### Phase A — Fix Immediately (No New Factors)

Edge corrections only. Zero cost, immediate improvement:

1. Reverse 13 backwards edges
2. Change 12 wrong signs to (±) or correct sign
3. Remove 14 spurious/tautological edges
4. Add 27 critical missing edges
5. ~~Wire Container Shipping Rates (Factor #108)~~ — **Done** (8 edges added)
6. Resolve China Property sign convention
7. Make 11 edge pairs bidirectional with lag differentiation

**Estimated impact:** Eliminates the most dangerous false cascade directions. The graph goes from "frequently misleading" to "directionally correct."

#### Phase B — Critical Factor Changes

1. Add 7 Priority 1 factors with full edge sets
2. Replace TED Spread with FRA-OIS Spread
3. Replace GBP/USD with AUD/USD
4. Replace Productivity with Unit Labor Costs
5. Execute 8 merges and 4 removals
6. Re-wire affected edges

**Estimated impact:** Closes the plumbing gap (the single worst domain). Adds OPEC+ and Retail Sales — two obviously-missing factors. Net factor count decreases slightly while analytical power increases significantly.

#### Phase C — Structural Improvements

1. Implement regime-dependent edge signs (Growth / Inflation / Crisis)
2. Implement non-linear threshold multipliers on 10 identified edges
3. Split EM into 3 regional sub-factors (if budget allows)
4. Add Priority 2 factors as data sources become available
5. Implement lag differentiation for bidirectional pairs
6. Add regime-dependent decay rates for feedback loops (30% normal, 10% crisis)

**Estimated impact:** Transforms the system from a fair-weather tool that confirms what you already know into a crisis-capable surveillance system that provides actionable intelligence when markets are breaking. This is where the investment pays off.

---

### Final Verdict

The framework's fundamental architecture — a directed causal graph with weighted propagation, scenario injection, and "generate first, map second" design — is sound. The factor selection is 80% correct. The problems are in the wiring: reversed edges, static signs, missing plumbing, and the systematic confusion of indicators with causes.

The good news is that every issue identified here is fixable without redesigning the graph. Phase A (edge corrections) can be done in a day and immediately improves every cascade the system produces. Phase B (factor changes) requires data source integration but addresses the most dangerous blind spots. Phase C (regime sensitivity) is the hardest but highest-leverage improvement — the difference between a tool that works in calm markets and one that works when markets are on fire.

A macro surveillance system that only works in calm markets is worthless. You don't need a system to tell you everything is fine when everything is fine. You need it to work on the day the repo market blows up, the yen carry trade unwinds, or the Treasury auction fails. That is what Phase C delivers.

---

## Transition Matrix Completeness Audit

Six domain-expert analysts independently reviewed the 110×110 transition matrix, systematically scanning every (source, target) pair to determine whether a direct causal transmission mechanism exists. This section consolidates their findings.

### Audit Statistics

| Metric | Value |
|--------|-------|
| Matrix dimensions | 110 × 110 = 12,100 entries |
| Non-zero entries before audit | ~1,067 (~8.8% density) |
| Missing edges identified | ~850 across all 6 domain teams |
| Spurious edges flagged | ~39 (mostly in commodities and flows) |
| Net new edges recommended | ~811 |
| Projected non-zero entries after audit | ~1,878 (~15.5% density) |
| Spurious edge rate in original matrix | ~3.7% (39/1,067) |

### Key Finding: The Graph is Accurate but Severely Under-Connected

All six analysts independently reached the same conclusion: **zero spurious edges were found in the macro, monetary policy, and rates blocks** — the core of the graph is economically sound. Spurious edges were concentrated in commodity cross-correlations (Cu→Iron Ore, Oil→Gold, Cu→Semis — common factor exposure, not causation) and in the flows block (where dependent variables are treated as causes).

The primary problem is **missing edges**, not wrong edges. The graph captures the skeleton of global macro transmission but misses the connective tissue — particularly in:

1. **EM contagion channels** — nearly every monetary/rates/vol factor is missing edges to EM Sovereign Spread, EM FX, and EM Equities
2. **Volatility transmission** — VIX, MOVE, and FX Vol are under-connected from upstream macro/credit stress factors
3. **Financial conditions feedback** — FCI should connect to nearly all real economy and asset price nodes
4. **Fund flow mechanics** — Fund Flows, ETF Flows, and Institutional Positioning are missing connections from most factors that drive allocation decisions
5. **Global equity linkages** — US ↔ Europe ↔ Japan ↔ China ↔ EM equity transmission is thin
6. **Safe-haven rotation** — VIX/CDS stress → Gold, DXY, Treasuries channels are largely absent

### Results by Domain Team

#### Team 1: Macro Economist (21 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| Fed Funds Rate | 23 | 21 | 0 |
| CPI | 9 | 13 | 0 |
| GDP | 13 | 15 | 0 |
| Unemployment | 9 | 10 | 0 |
| Manufacturing PMI | 8 | 11 | 0 |
| PCE | 6 | 11 | 0 |
| Consumer Confidence | 5 | 8 | 0 |
| Wage Growth | 6 | 9 | 0 |
| Jobless Claims | 7 | 6 | 0 |
| Services PMI | 8 | 6 | 0 |
| Productivity | 7 | 6 | 0 |
| JOLTS | 5 | 5 | 0 |
| Participation | 6 | 5 | 0 |
| Fiscal Deficit | 12 | 9 | 0 |
| Debt/GDP | 10 | 8 | 0 |
| Treasury Issuance | 11 | 10 | 0 |
| Govt Spending | 12 | 10 | 0 |
| Housing Starts | 6 | 9 | 0 |
| Home Prices | 9 | 7 | 0 |
| Mortgage Rate | 8 | 6 | 0 |
| CRE Stress | 9 | 8 | 0 |
| **Subtotal** | **189** | **193** | **0** |

**Highest-priority additions:** Fed Funds Rate → Repo/SOFR (administrative anchor), FFR → Financials/Regional Banks (NIM), FFR → Money Market Fund Flows (yield differential), CRE → REITs, GDP → 10Y Yield.

**Systematic gaps:** Rate Expectations missing from many macro data factors. Revenue/Earnings edges missing from demand-side factors. Currency pair edges beyond DXY under-represented.

#### Team 2: Monetary Policy Specialist (14 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| Fed Balance Sheet | 11 | 14 | 1 |
| Rate Expectations | 14 | 15 | 0 |
| QE Pace | 12 | 11 | 0 |
| Global CB Liquidity | 12 | 13 | 0 |
| ECB Rate | 8 | 11 | 0 |
| PBOC Policy | 10 | 12 | 0 |
| Term Premium | 11 | 12 | 0 |
| FCI | 11 | 17 | 0 |
| Lending Standards | 10 | 13 | 0 |
| Bank Reserves | 7 | 9 | 1 |
| Repo/SOFR | 8 | 10 | 1 |
| TED Spread | 8 | 11 | 0 |
| CP Spread | 7 | 10 | 2 |
| MMF Flows | 7 | 10 | 2 |
| **Subtotal** | **136** | **168** | **7** |

**Highest-priority additions:** FCI → Unemployment/CPI/Manufacturing PMI (real economy transmission), Rate Expectations → HY Spread/MOVE/VIX, Term Premium → HY Spread/NASDAQ, PBOC → China Equities/Oil/Lithium.

**Spurious flags:** Fed Balance Sheet → Bitcoin (indirect via FCI), Bank Reserves → S&P 500 (indirect via FCI), Repo/SOFR → Bank Reserves (direction reversed), CP Spread → Revenue (too indirect).

#### Team 3: Rates & Credit Strategist (12 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| 2Y Yield | 12 | 11 | 0 |
| 10Y Yield | 20 | 19 | 0 |
| 30Y Yield | 7 | 7 | 0 |
| Yield Curve | 9 | 6 | 0 |
| IG Spread | 10 | 9 | 0 |
| HY Spread | 12 | 10 | 0 |
| Real Yield | 12 | 12 | 0 |
| Breakevens | 10 | 10 | 0 |
| 5Y5Y Forward | 5 | 5 | 0 |
| EM Sovereign Spread | 7 | 7 | 0 |
| Private Credit | 8 | 8 | 0 |
| CRE Stress | 9 | 9 | 0 |
| **Subtotal** | **121** | **113** | **0** |

**Note:** This team found zero spurious edges. The rates & credit block is the most accurately wired domain in the graph. The gaps are entirely missing connections, not wrong ones.

**Highest-priority additions:** 10Y Yield → all 19 missing targets (this is the single most important node in global finance), HY Spread → Russell 2000/Lending Standards/Energy Sector, Real Yield → all 12 targets.

#### Team 4: Geopolitics & Global Macro (17 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| Geopolitical Risk | 15 | 32 | 0 |
| Trade Policy | 18 | 28 | 0 |
| US Political Risk | 13 | 32 | 0 |
| Sanctions | 13 | 36 | 0 |
| Climate Policy | 15 | 30 | 1 |
| Tech Regulation | 11 | 16 | 1 |
| Supply Chain Pressure | 15 | 27 | 0 |
| Baltic Dry | 10 | 14 | 0 |
| Container Shipping | 8 | 26 | 0 |
| China PMI | 9 | 32 | 0 |
| EU HICP | 6 | 24 | 2 |
| BOJ Policy | 7 | 25 | 0 |
| China Credit Impulse | 11 | 29 | 1 |
| China Property | 9 | 32 | 0 |
| EU Periphery Spreads | 8 | 31 | 0 |
| Global Trade Volume | 10 | 31 | 0 |
| India Growth | 7 | 35 | 0 |
| **Subtotal** | **185** | **~480** | **5** |

**Note:** This team identified the most missing edges by far. Geopolitical and global factors are the most under-connected domain — they currently have narrow edge sets but should be broadly connected since geopolitical shocks propagate across all asset classes simultaneously.

**Highest-priority additions:** All sources → Financials, Russell 2000, Fund Flows, VIX, HY Spread, DXY, Lending Standards. Container Shipping (recently wired with 8 edges) needs ~26 more. India Growth at 7 edges needs ~35 more.

**Direction errors found:** EU HICP → Natural Gas (reversed — gas drives HICP), China Credit Impulse → PBOC Policy (reversed — PBOC drives credit).

#### Team 5: Equity & Volatility Specialist (25 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| S&P 500 | 18 | ~30 | 0 |
| NASDAQ | 7 | ~18 | 0 |
| Tech Sector | 6 | ~17 | 0 |
| Energy Sector | 5 | ~18 | 0 |
| Financials | 7 | ~22 | 0 |
| Russell 2000 | 6 | ~15 | 0 |
| Healthcare | 3 | ~15 | 0 |
| REITs | 4 | ~13 | 0 |
| Regional Banks | 6 | ~18 | 0 |
| EM Equities | 5 | ~15 | 0 |
| Europe Equities | 4 | ~16 | 0 |
| China Equities | 8 | ~22 | 0 |
| Japan Equities | 4 | ~16 | 0 |
| Semiconductors | 7 | ~18 | 0 |
| Earnings | 10 | ~19 | 0 |
| PE Valuations | 6 | ~15 | 0 |
| Revenue | 6 | ~16 | 0 |
| ERP | 4 | ~15 | 0 |
| Buybacks | 5 | ~13 | 0 |
| VIX | 17 | ~32 | 0 |
| MOVE | 11 | ~28 | 0 |
| Put/Call | 5 | ~10 | 0 |
| SKEW | 4 | ~13 | 0 |
| CDS | 11 | ~27 | 0 |
| FX Vol | 9 | ~27 | 0 |
| **Subtotal** | **183** | **~448** | **0** |

**Note:** Zero spurious edges found. The equity/vol block is correctly wired but drastically under-connected.

**Key themes:** Cross-asset contagion systematically under-represented (equity→credit, equity→rates, equity→FX). Safe-haven rotation channels absent (VIX→Gold, VIX→DXY, VIX→Treasuries). Real economy feedback loops missing (equity/credit stress → GDP, Unemployment, Consumer Confidence, Lending Standards). Fund flow mechanics sparse.

#### Team 6: FX, Commodities & Flows (23 source factors)

| Source Factor | Current Edges | Missing Edges | Spurious |
|---|---|---|---|
| DXY | 18 | 13 | 1 |
| EUR/USD | 7 | 7 | 0 |
| USD/JPY | 8 | 6 | 0 |
| USD/CNY | 12 | 7 | 0 |
| GBP/USD | 5 | 7 | 1 |
| EM FX | 10 | 7 | 1 |
| Bitcoin | 7 | 6 | 1 |
| Oil | 18 | 12 | 3 |
| Gold | 7 | 9 | 2 |
| Copper | 10 | 9 | 2 |
| Natural Gas | 11 | 10 | 2 |
| Wheat | 8 | 3 | 2 |
| Soybeans | 8 | 4 | 2 |
| Iron Ore | 9 | 6 | 3 |
| Lithium | 7 | 1 | 4 |
| Uranium | 6 | 4 | 3 |
| Silver | 5 | 6 | 3 |
| Retail Sentiment | 9 | 6 | 1 |
| Fund Flows | 8 | 9 | 2 |
| Institutional Positioning | 7 | 10 | 1 |
| Margin Debt | 8 | 7 | 2 |
| ETF Flows | 10 | 10 | 0 |
| IPO Issuance | 7 | 7 | 3 |
| **Subtotal** | **205** | **166** | **39** |

**Note:** This team found the most spurious edges (39), concentrated in:
- **Commodity cross-correlations** (Cu→Iron Ore, Cu→Lithium, Cu→Semis, Oil→Gold, Oil→Soybeans, Oil→Fiscal Deficit) — common factor exposure, not direct causation
- **Niche commodity over-connection** (Lithium: 4 spurious, Uranium: 3, Silver: 3) — these small markets don't have direct transmission mechanisms to many of their listed targets
- **Direction reversals** (Wheat→Geopolitical Risk, Soybeans→USD/CNY, Iron Ore→CPI — all backwards)
- **IPO Issuance** treated as cause rather than effect (IPO→PE, IPO→ERP, IPO→Private Credit all spurious)

### Consolidated Spurious Edge List (39 Edges to Review/Remove)

| Source | Target | Issue |
|--------|--------|-------|
| Cu → Iron Ore | Common factor (China demand) | Remove |
| Cu → Semiconductors | Common factor (global cycle) | Remove |
| Cu → Lithium | Narrative correlation, no transmission | Remove |
| Cu → CPI | Negligible CPI component | Remove |
| Oil → Gold | Common factor (USD, inflation) | Remove |
| Oil → Soybeans | Too indirect (fertilizer chain is 3+ hops) | Review |
| Oil → Fiscal Deficit | Too indirect for US | Review |
| Gold → Bitcoin | No direct mechanism | Remove |
| Gold → Mining Equities | Not in 110-factor list | Remove |
| Iron Ore → CPI | Negligible US CPI impact | Remove |
| Iron Ore → Housing Starts | US uses wood-frame, not steel | Review |
| Iron Ore → Copper | Common factor, not causal | Remove |
| Lithium → Semiconductors | Different supply chains | Remove |
| Lithium → Copper | No direct mechanism | Remove |
| Lithium → China PMI | Too small to move PMI | Remove |
| Lithium → EM Equities | Too indirect | Review |
| Uranium → EM Sovereign Spread | Too indirect | Remove |
| Uranium → Geopolitical Risk | Reversed causality | Remove |
| Uranium → Sanctions | Reversed causality | Remove |
| Silver → Semiconductors | Negligible input cost | Remove |
| Silver → EM Equities | No direct mechanism | Remove |
| Silver → CPI | Zero CPI weight | Remove |
| Natural Gas → Housing Starts | Very weak connection | Review |
| Natural Gas → Uranium | Extremely slow substitution | Review |
| Wheat → Geopolitical Risk | Reversed causality | Remove |
| Wheat → India Growth | Too indirect | Review |
| Soybeans → USD/CNY | Reversed causality | Remove |
| Soybeans → China PMI | Too indirect | Remove |
| GBP/USD → US Political Risk | Reversed causality | Remove |
| EM FX → Copper | Reversed causality | Remove |
| DXY → Earnings | Too indirect | Review |
| Bitcoin → Gold | No direct mechanism | Remove |
| Retail Sentiment → IPO Issuance | Reversed causality | Remove |
| IPO → Private Credit | No direct mechanism | Remove |
| IPO → ERP | Derived metric, not causal | Remove |
| IPO → PE | Negligible dilution effect | Remove |
| Fund Flows → PE | Indirect (via equity prices) | Remove |
| Fund Flows → ETF Flows | Near-tautological overlap | Review |
| Margin Debt → FCI | Input, not cause | Review |

### Audit Conclusion

The transition matrix is **accurate at its core** — the original ~1,067 edges represent legitimate causal mechanisms with only ~39 spurious entries (~3.7% error rate). However, the matrix is **dramatically under-connected** — six independent expert teams identified ~850 missing edges, which would nearly double the matrix density from 8.8% to ~15.5%.

The pattern is consistent: the original edge mapping captured the strongest, most obvious transmission mechanisms but missed the secondary channels that create the connective tissue of cross-asset contagion. In calm markets, the missing edges are invisible. In crises — when correlations spike and transmission mechanisms fire simultaneously — these missing connections are the difference between a system that explains what happened and one that predicts what's about to happen.

---

## Conclusion

These 110 factors and their interconnections represent our best assessment of what a comprehensive macro surveillance system requires. The framework is designed to be **complete without being exhaustive** — every factor earns its place through historical precedent, transmission mechanism importance, or structural risk monitoring.

The key principle is not to predict the future — it is to **understand the present quickly enough to respond.** When the next crisis hits, we need to be able to trace the causal chain from trigger to consequence within hours, not weeks. This factor graph is the tool that makes that possible.

The gaps we identified in the previous 52-node system — housing, financial plumbing, China depth, EM contagion, fiscal policy, real yields — are not academic concerns. They are the categories that produced the largest market dislocations of the last 20 years. Closing these gaps is not an enhancement. It is a correction of a critical vulnerability.

---

*End of Report*
