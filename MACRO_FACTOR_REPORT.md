# Global Macro Impact Factor Framework

**Causal Sentiment — Factor Selection Report**
*Global Macro Research Desk*
*March 2026*

---

## Executive Summary

This report documents the 111 macro impact factors selected for our causal factor graph — the analytical backbone of our macro surveillance system. These are not investment style factors (value, momentum, carry). These are the **structural forces that move global financial markets**: the rates decisions, the credit impulses, the geopolitical shocks, the plumbing failures, the housing cycles, and the contagion chains that, when they break, produce the events that define decades.

We designed this framework with a single test: **can we trace every major market dislocation of the last 20 years through these factors?** The 2008 financial crisis. The European sovereign debt crisis. COVID. SVB. The AI boom. The yen carry unwind. If the answer is no — if a crisis happened and our graph has no path to explain it — then we have a blind spot that will cost us when the next variant of that crisis arrives.

The result is 111 factors across 17 categories, connected by over 1,000 directed causal edges — each validated by domain expert review. Each factor earned its place by satisfying at least one of three criteria:

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

### Category 7: Equities (14 Factors)

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

**67. Japan Equities (Nikkei)** *(NEW)*
We include this because Japan is the **world's largest creditor nation with $3.1 trillion in foreign assets**, and the Nikkei is the barometer of the yen carry trade that connects BOJ policy to global risk assets. When the BOJ kept rates at zero for decades, Japanese investors poured capital into US Treasuries, European bonds, and EM debt — funding a global carry trade estimated at $500B-$1T. The Nikkei's 80% decline from 1989 to 2003 was the longest bear market in modern history. Its breakout above the 1989 high in 2024 — powered by corporate governance reform, a weak yen, and Warren Buffett's endorsement — was a structural regime change. Japan's semiconductor industry (Tokyo Electron, Renesas, Screen Holdings) is critical to the global chip supply chain. The August 5, 2024 crash (Nikkei −12.4% in a single session, the worst since 1987 Black Monday) demonstrated that Japanese equity moves can cascade globally within hours via the carry trade unwind mechanism. Without a Japan equities node, our graph captures the BOJ policy shift and the yen move but cannot trace the equity market consequence or the wealth effect on Japanese institutional investors who are the world's largest foreign bondholders.

---

### Category 8: Equity Fundamentals (5 Factors)

**Why this category exists:** Prices can deviate from fundamentals for years, but eventually earnings, valuations, and margins *matter*. When the S&P 500 trades at 22x forward earnings with a 2.5% real yield, the equity risk premium is near zero — meaning stocks offer no excess compensation for risk. That is a regime-defining signal that affects expected returns for every allocator in the world.

**68. Earnings Momentum**
Earnings revision breadth — the percentage of companies seeing upward vs. downward revisions. This is a leading indicator for actual earnings (and therefore equity returns). Momentum shifted negative in Q3 2022 (signaling the earnings recession) and positive in Q1 2023 (signaling recovery). It moves before earnings are reported.

**69. P/E Valuations**
Forward P/E ratio for the S&P 500. Not a timing tool, but a *vulnerability* indicator. At 22x earnings, a 10% earnings miss or a 50bp rise in real yields can cause a 15%+ drawdown. At 15x, the same shock causes a 5% dip. Valuations determine the *severity* of selloffs, not their timing.

**70. Revenue Growth**
Top-line growth is harder to engineer through buybacks, accounting, or margin expansion. When revenue growth decelerates, it signals genuine demand weakness rather than financial engineering running out of road. Revenue growth turned negative in Q1 2023 for the first time since COVID, correctly signaling the manufacturing recession.

**71. Equity Risk Premium** *(NEW)*
We include this because it is the **single number that tells you whether equities are attractive relative to bonds.** Defined as earnings yield (1/PE) minus real yield (TIPS). When the ERP is 5%+ (as in 2009, 2020), stocks are being given away relative to bonds. When it's near zero (as in late 2023, early 2024), there is no compensation for owning equities over the risk-free asset. This measure collapsed from 4%+ in 2020 to near zero in 2024, which is why the "higher for longer" regime is so dangerous for equities — bonds became competitive for the first time in 15 years. Every asset allocator in the world is watching this number.

**72. Corporate Buybacks** *(NEW)*
We include this because buybacks are the **single largest source of US equity demand** — roughly $1 trillion per year for S&P 500 companies. When buybacks are running (most of the year), they provide a bid under the market. When they stop (earnings blackout windows, credit tightening, tax policy changes), the bid disappears. The 2019 proposal to tax buybacks and the 2022 1% excise tax both moved markets. Buyback activity is also a signal of corporate confidence: companies buy back stock when they believe their shares are cheap and their future is bright.

---

### Category 9: Currencies (7 Factors)

**Why this category exists:** Currencies are the relative price of one country's monetary policy, growth, and risk against another's. They are also the *mechanism* through which US monetary policy is exported to the world. When the Fed hikes and the dollar strengthens, every country with dollar-denominated debt faces tighter financial conditions regardless of their own central bank's actions. The dollar is the world's reserve currency, and DXY strength/weakness is a global financial conditions indicator.

**73. US Dollar Index (DXY)**
The single most important currency indicator. DXY strength correlates with: tighter global financial conditions, weaker commodities, weaker EM assets, and compressing US multinational earnings (translation effect). DXY weakening correlates with: easier global conditions, commodity rallies, EM equity outperformance. The 2022 DXY surge (to 20-year highs) was the mechanism through which US rate hikes were transmitted globally.

**74-76. EUR/USD, USD/JPY, USD/CNY**
The three most systemically important bilateral exchange rates. EUR/USD — ECB vs. Fed policy divergence, European economic health, energy security. USD/JPY — carry trade dynamics, BOJ policy, Japan's $1.3T in US Treasury holdings. USD/CNY — trade tensions, China's managed exchange rate as a policy tool, capital flow signal. Each pair has a distinct driver set and a distinct contagion pathway.

**77. GBP/USD** *(NEW)*
We include this because the UK is a **distinct macro entity with its own crisis dynamics.** The September 2022 "Truss mini-budget" crashed GBP by 10% in days and triggered a pension fund liquidity crisis that forced the BOE to intervene. Brexit created permanent trade friction. The BOE's divergence from the Fed (cutting while the Fed was on hold, or vice versa) creates distinct GBP dynamics. As a G10 reserve currency, GBP distress is a signal of broader "fiscal credibility" risk — if it can happen to the UK, markets ask whether it can happen to others.

**78. EM FX Basket** *(NEW)*
We include this because **EM currency stress is the first signal of EM crisis.** Before EM sovereign spreads blow out, before EM equities crash, EM currencies weaken. The Turkish lira's 50% collapse preceded Turkey's inflation and banking crisis. The Argentine peso's crawling peg break preceded the sovereign default. An aggregate EM FX basket captures the collective stress across dozens of EM economies, weighted by importance. This is the early warning system for EM contagion.

**79. Bitcoin** *(NEW)*
We include this because Bitcoin is now a **$1 trillion+ asset class with material institutional adoption.** The launch of spot Bitcoin ETFs in January 2024 brought $50B+ in flows, making Bitcoin allocation decisions relevant for mainstream asset managers. Bitcoin's correlation regime shifts: in risk-on environments, it trades like "leveraged NASDAQ" (correlated with tech); in dollar-weakness environments, it trades like "digital gold" (correlated with gold and inverse DXY); in liquidity crises, it crashes alongside all risk assets. Bitcoin is also a proxy for global liquidity conditions and speculative risk appetite. A macro system ignoring a $1T+ asset that institutional investors now hold is willfully blind.

---

### Category 10: Flows & Sentiment (5 Factors)

**Why this category exists:** Fundamentals tell you what *should* happen. Flows and positioning tell you what *is* happening and what *will* happen mechanically. If every hedge fund is long the same trade and the trade goes against them, the forced selling creates a crash regardless of fundamentals. The Yen carry trade unwind in August 2024 was a *positioning* event, not a fundamental event — and it caused a 12% crash in Japanese equities and a 3% drop in the S&P in a single day.

**80. Retail Sentiment**
Social media, survey-based, and options flow indicators of retail investor behavior. Retail sentiment is a contrarian indicator at extremes: when retail is euphoric (crypto in November 2021, meme stocks in January 2021), markets are near tops. When retail capitulates (December 2022 crypto, March 2020 equities), markets are near bottoms. The signal is in the extremes, not the level.

**81. Fund Flows**
Net flows into equity, bond, and money market funds. Tells you what investors are actually *doing* with their money (vs. what surveys say they're thinking). The rotation from money market funds back into equities in late 2023 was a key driver of the Q4 rally. Record flows out of bond funds in 2022 amplified the selloff.

**82. Institutional Positioning (COT)**
CFTC Commitment of Traders data. Shows net speculative positioning in futures markets. When speculators are max long equities and max short bonds, the *mechanical* risk is a reversal — any shock forces position unwinds that amplify the move. The August 2024 yen carry unwind was partially caused by *extreme* speculative short JPY positioning unwinding simultaneously.

**83. Margin Debt / Leverage** *(NEW)*
We include this because **leverage is the amplifier that turns corrections into crashes.** FINRA margin debt peaked at $936B in October 2021 — the same month as the market top. Margin calls force selling, which causes more margin calls, which forces more selling. This is the self-reinforcing feedback loop that turned the 2020 COVID selloff into a -34% crash in 23 trading days. Separately, total system leverage (including options, futures, and prime brokerage lending) determines how fragile the market is to shocks. A 2% correction in a low-leverage regime is a buying opportunity. A 2% correction in a high-leverage regime is a potential crash trigger.

**84. ETF Flows** *(NEW)*
We include this because **passive investing has fundamentally changed market structure.** Over 50% of US equity assets are now in passive/index vehicles. ETF creation and redemption flows mechanically move underlying stock prices — when $1B flows into SPY, it buys every S&P 500 stock proportionally regardless of valuation. This creates momentum effects (inflows beget price increases beget more inflows), concentration risk (the biggest stocks get the biggest flows), and correlation risk (all stocks in an index move together). ETF flow data tells us whether the "passive bid" is supporting or withdrawing from the market.

---

### Category 11: Global (8 Factors)

**Why this category exists:** The US is 26% of global GDP but 60%+ of global equity market cap. This means our US-centric categories above describe the dominant financial market, but not the dominant economy. China's 18% of global GDP, the Eurozone's 15%, India's growing share, and the collective EM 40%+ share drive commodity demand, supply chain dynamics, and global growth expectations. A US-only macro model would have missed the 2011 European debt crisis, the 2015 China devaluation, and the 2022 European energy crisis.

**85. China PMI**
China is the world's manufacturing floor. China PMI leads global trade volumes, commodity demand, and EM growth expectations. A move from 49 to 52 in China PMI is a more powerful global growth signal than a move from 52 to 55 in US PMI — because China's marginal commodity consumption is massive.

**86. EU HICP**
Eurozone inflation drives ECB policy, which drives EUR/USD, which drives global dollar conditions. EU HICP hit 10.6% in October 2022 (driven by energy), forcing the ECB to hike aggressively even as the European economy contracted — a "stagflation" dynamic unique to Europe.

**87. BOJ Policy**
Japan is the world's largest creditor nation with $3.1T in foreign assets. BOJ yield curve control kept Japanese 10Y yields near 0% for years, driving a massive carry trade (borrow in JPY, invest in higher-yielding assets globally). When the BOJ loosened YCC in 2023 and raised rates in 2024, it triggered the yen carry unwind — the most violent single-day equity move of 2024. BOJ policy changes have outsized global impact because of Japan's accumulated foreign positions.

**88. China Credit Impulse** *(NEW)*
We include this because the China credit impulse — the change in total social financing as a percentage of GDP — is **the single best leading indicator for global industrial activity.** It leads global PMIs by 6-9 months. It leads commodity prices. It leads EM equity performance. The mechanism is direct: when Chinese banks and shadow banks extend more credit, that credit funds construction, infrastructure, and manufacturing expansion, which drives demand for iron ore, copper, oil, and every other industrial commodity. The credit impulse turned negative in late 2021, correctly predicting the global manufacturing slowdown that followed. Without this factor, we cannot forecast the direction of global growth.

**89. China Property Sector** *(NEW)*
We include this because China's property sector is approximately **30% of GDP** (including related industries), and its crisis is the largest ongoing structural risk in the global economy. Evergrande's default in 2021, Country Garden's collapse in 2023, and the ongoing developer debt restructuring have destroyed household wealth (70%+ of Chinese household assets are in property), depressed consumer confidence, and created deflationary pressure. The property crisis cascades through: iron ore (construction demand), copper (wiring), Australian dollar (mining exports to China), and global growth expectations. Our system previously had no way to monitor this — the most important single-sector risk in the world economy.

**90. EU Periphery Spreads (Italy-Germany)** *(NEW)*
We include this because the **Eurozone fragmentation risk is existential and recurring.** The Italy-Germany 10Y spread measures whether the market believes the Eurozone will stay together. When it blew out to 550bp in 2011, the Euro nearly collapsed. When it spiked in 2018 (Italian budget crisis) and 2022 (ECB tightening), the ECB had to invent new tools (TPI) to contain it. This spread is the barometer of European institutional credibility. If it goes above 300bp, the ECB is forced into crisis mode regardless of inflation, and EUR/USD collapses — making it a first-order macro driver.

**91. Global Trade Volume** *(NEW)*
We include this because **trade contraction has preceded every global recession since WWII.** The WTO/CPB world trade monitor captures the volume of goods crossing borders — stripped of price effects. Trade volume collapsed 15% in 2020 (COVID), declined in 2019 (tariff war), and is under pressure again in 2025 (new tariff escalation). For export-dependent economies (Germany, Japan, South Korea, most of EM), trade volume is more important than US GDP growth. It also serves as a real-time check on whether tariff policies are actually reducing trade or merely rerouting it.

**92. India Growth** *(NEW)*
We include this because India is the **5th largest economy and the fastest-growing major economy**, projected to become the 3rd largest by 2028. India's growth drives distinct commodity demand (especially oil — India is the 3rd largest importer), technology services demand, and an emerging consumer market. India's economic trajectory is increasingly relevant for global allocators: MSCI recently increased India's weight in EM indices, and foreign institutional flows into India are becoming material. This factor also captures the "China+1" supply chain diversification theme.

---

### Category 12: Housing / Real Estate (4 Factors) — NEW

**Why this category exists:** The 2008 Global Financial Crisis — the worst financial disaster since the Great Depression — was a **housing** crisis. The entire global financial system nearly collapsed because of US residential mortgage defaults. And yet, our factor graph had zero housing factors. Housing is the most interest rate-sensitive sector of the economy, the largest component of household wealth (65%+ for median households), and the largest component of CPI (shelter inflation is 40% of CPI). Any macro surveillance system without housing is like a fire alarm with no smoke detector.

**93. US Housing Starts** *(NEW)*
We include this because housing starts are the **most interest rate-sensitive leading indicator of economic activity.** When mortgage rates doubled from 3% to 7% in 2022, housing starts dropped 25% — the fastest decline since 2008. Housing construction drives employment (residential construction is 3-4% of GDP), materials demand (lumber, copper, concrete), and GDP. Starts lead GDP by 2-3 quarters because a house that breaks ground today generates economic activity for 6-12 months.

**94. US Home Prices (Case-Shiller)** *(NEW)*
We include this because home prices are the **primary transmission mechanism of the wealth effect** — when home prices rise, homeowners feel wealthier and spend more. US residential real estate is worth ~$45 trillion, making it the largest asset class in the world. Home prices also *directly* feed into CPI via shelter/rent inflation (owners' equivalent rent is 26% of CPI). The 2006-2012 home price decline of 27% destroyed $7 trillion in household wealth and triggered the GFC. The 2020-2022 surge of 40% created a wealth effect that helped sustain consumer spending even as the Fed tightened. You cannot model US inflation or US consumption without modeling home prices.

**95. 30-Year Mortgage Rate** *(NEW)*
We include this because mortgage rates are the **direct transmission mechanism from Fed policy to housing activity and consumer spending.** The mortgage rate moved from 2.65% (January 2021) to 7.79% (October 2023) — a tripling that had never happened before in such a short period. This made monthly payments on a median-priced home 60% more expensive, freezing the existing home market (homeowners refused to sell and give up their 3% mortgages) while crushing new home affordability. The "mortgage rate lock-in" effect is constraining labor mobility, housing supply, and household formation. This is the most consequential Fed transmission channel for the average American.

**96. Commercial Real Estate Stress** *(NEW)*
We include this because CRE is the **slow-moving crisis that the financial system is struggling to acknowledge.** Office vacancy rates are above 20% in major cities. Work-from-home is a permanent structural shift, not a pandemic anomaly. CRE loans represent 30% of regional bank assets — the same banks that nearly failed during SVB. CRE valuations are marked at appraisal values that lag market reality by 12-18 months. The disconnect between market prices (REIT indices down 30%+) and bank book values (barely marked down) is a solvency illusion. When the "extend and pretend" strategy on CRE loans expires (most loans are 5-7 year term), banks will face realized losses. This is the risk that kept the 2023 banking crisis from being declared "over."

---

### Category 13: Financial System / Banking (4 Factors) — NEW

**Why this category exists:** The financial system is the **plumbing** of the economy. When plumbing works, no one thinks about it. When it fails, everything stops. The 2008 GFC, the 2019 repo crisis, the 2020 COVID liquidity crunch, and the 2023 SVB collapse were all *plumbing* failures. Yet our system had no visibility into bank lending conditions, reserve levels, funding stress, or aggregate financial conditions. We were monitoring the house's temperature (inflation, GDP) without checking whether the pipes were frozen.

**97. Financial Conditions Index** *(NEW)*
We include this because the Chicago Fed National Financial Conditions Index is the **single best aggregate measure of whether financial conditions are loose or tight.** It integrates 105 indicators: interest rates, credit spreads, equity prices, dollar strength, money supply, bank lending, and volatility into one number. When the FCI tightens rapidly (as in Q4 2018, March 2020, Q3 2022), risk assets sell off. When it loosens (as in Q4 2023), risk assets rally. Fed officials watch the FCI to gauge whether their rate hikes are *actually* tightening conditions — because sometimes the market rallies through rate hikes (2023), effectively loosening conditions and undermining the Fed's intentions.

**98. Bank Lending Standards** *(NEW)*
We include this because the Fed Senior Loan Officer Opinion Survey (SLOOS) is the **most reliable predictor of credit availability to the real economy.** When banks tighten lending standards, businesses can't get loans, consumers can't get mortgages, and economic activity contracts — regardless of what the Fed funds rate is. Tightening lending standards preceded every US recession since 1990. After SVB, bank lending standards tightened to GFC levels — equivalent to ~50bp of additional rate hikes that the Fed didn't have to implement. This is the "shadow tightening" that models miss if they only watch the fed funds rate.

**99. Bank Reserves at the Fed** *(NEW)*
We include this because reserve adequacy determines whether **the money market plumbing functions or seizes.** In September 2019, the repo market blew up (overnight rates spiked from 2% to 10%) because the Fed had drained reserves too far via QT. The Fed had to emergency-inject $75B/day to stabilize the system. As QT continues in 2024-25, the question is: when do reserves again hit the "scarcity" threshold? If the answer is "unexpectedly," we get another plumbing crisis. Monitoring reserves allows us to estimate the proximity of this cliff.

**100. Repo / SOFR Rate** *(NEW)*
We include this because SOFR (Secured Overnight Financing Rate) is the **heartbeat of the financial system.** It replaced LIBOR as the benchmark for $400T+ in financial contracts. When SOFR is stable and close to the fed funds rate, the plumbing is healthy. When SOFR spikes above the fed funds rate, it signals funding stress — banks or institutions are willing to pay a premium for overnight cash, which means someone is in trouble. The September 2019 repo crisis was visible in SOFR days before the Fed acknowledged it. March 2020 saw SOFR dislocations before the Fed's emergency interventions. This is our real-time stress sensor for the financial plumbing.

---

### Category 14: Money Markets / Funding (3 Factors) — NEW

**Why this category exists:** Money markets are where the financial system funds itself *overnight*. When money markets work, no one outside of fixed income trading desks cares. When they freeze, the financial system dies within days. The commercial paper market freezing in September 2008 is what turned a housing crisis into a global financial crisis — companies like GE could not roll their short-term debt. The Fed's emergency facilities in 2020 (CPFF, PDCF, MMLF) were all designed to unfreeze money markets. This is a distinct category from "Financial System" because money market stress operates on a different timescale (days, not months) and requires different interventions.

**101. TED Spread (SOFR-Treasury)** *(NEW)*
We include this because the TED spread (modernized as SOFR minus T-bill) is the **fastest real-time indicator of counterparty and funding stress.** It measures how much more banks charge each other for unsecured lending compared to lending to the US government. During the GFC, TED spread hit 450bp (banks didn't trust each other). During COVID, it spiked to 140bp. During SVB, it jumped 50bp in two days. A persistently elevated TED spread means the banking system is under stress — even if no individual bank has failed yet. It's the smoke detector for the next banking crisis.

**102. Money Market Fund Flows** *(NEW)*
We include this because money market funds are now a **$6 trillion+ force** that can destabilize the banking system through deposit competition. During the SVB crisis, $500B flowed from bank deposits into money market funds in a single week — the largest deposit migration in history. This happened because MMFs were yielding 5%+ while most banks were still paying 0.5% on deposits. The flow from deposits to MMFs is a form of bank disintermediation that tightens credit availability. It also means that money market fund *outflows* (back into equities or bank deposits) are a major source of liquidity that can fuel rallies.

**103. Commercial Paper Spread** *(NEW)*
We include this because commercial paper is how **large corporations fund their day-to-day operations** — payroll, inventory, working capital. When CP spreads widen, it means the market is pricing higher risk that these companies can't roll their debt. When the CP market *freezes* (as in September 2008 and briefly in March 2020), companies face immediate liquidity crises regardless of their long-term solvency. The Fed created the Commercial Paper Funding Facility specifically because CP market dysfunction threatened to turn a financial crisis into an immediate corporate bankruptcy wave.

---

### Category 15: Fiscal Policy / Sovereign (3 Factors) — NEW

**Why this category exists:** We are living through the most aggressive fiscal expansion in peacetime history. The combination of COVID stimulus ($5T+), infrastructure spending ($1.2T), CHIPS Act ($280B), and IRA ($370B) has fundamentally altered the US fiscal trajectory. Fiscal deficits running at 6%+ of GDP during full employment are historically unprecedented. This has real consequences: more Treasury issuance, higher term premium, and a credibility question about long-run fiscal sustainability. The 2023 bond selloff was *primarily* about fiscal concerns, not inflation. A macro system that only watches the Fed but ignores Congress is missing half the policy picture.

**104. US Debt-to-GDP** *(NEW)*
We include this because **fiscal sustainability is a structural risk that constrains future policy options.** US federal debt exceeded 120% of GDP in 2024 — the highest since WWII. At current trajectory, interest payments will exceed defense spending by 2025. This matters because: (a) it limits the government's ability to stimulate during the next recession (fiscal space is constrained), (b) it raises questions about long-run dollar reserve currency status, and (c) it creates a self-reinforcing dynamic where higher rates → higher interest payments → larger deficits → more issuance → higher rates. We monitor this as a slow-moving structural constraint that defines the policy envelope.

**105. Treasury Issuance / Supply** *(NEW)*
We include this because **Treasury supply directly moves bond prices**, and the supply shock of 2023 was the proximate cause of the 10Y yield hitting 5%. When the Treasury refunding announcement in August 2023 revealed larger-than-expected issuance, yields rose 100bp in weeks. The market was asking: "who will buy an extra $1 trillion in Treasuries per year?" The answer was: "only at higher yields." This is a pure supply-demand dynamic that operates independently of monetary policy or inflation expectations. Net new Treasury supply is the marginal price setter for the world's risk-free rate.

**106. US Government Spending** *(NEW)*
We include this because the **fiscal impulse** (the change in government spending relative to GDP) is a major GDP growth driver that our system was ignoring. The IRA, CHIPS Act, and infrastructure bill collectively represent the largest US industrial policy since the Marshall Plan. Factory construction spending has doubled. Government contractors are on a hiring spree. This fiscal spending is one reason GDP growth remained robust despite 525bp of rate hikes — the government was stimulating while the Fed was braking. Without tracking government spending, our system attributes growth resilience entirely to consumer strength, missing the fiscal engine.

---

### Category 16: Supply Chain / Trade Infrastructure (3 Factors) — NEW

**Why this category exists:** The COVID pandemic taught the world that **supply chains are a macro force, not a logistics footnote.** Supply chain disruptions drove the 2021-22 inflation episode more than any demand-side factor. A single ship blocking the Suez Canal (March 2021) cost $10B/day in delayed trade. Houthi attacks in the Red Sea (2024) rerouted 30% of global container traffic. Semiconductor shortages shut down auto production lines worldwide. The lesson: supply chain disruptions transmit geopolitical shocks into inflation, corporate earnings, and GDP — and they can persist for years. A macro system without supply chain visibility is fighting the last war (demand-driven inflation of the 1970s) instead of the current one (supply-driven inflation of the 2020s).

**107. Supply Chain Pressure Index** *(NEW)*
We include this because the NY Fed Global Supply Chain Pressure Index is the **single best aggregate measure of supply chain stress.** It integrates shipping costs, delivery times, backlogs, and inventory data into one number. It peaked at 4.3 standard deviations above normal in December 2021 — the most extreme reading in its history. It then normalized through 2023, correctly signaling that goods inflation would decline. When Houthi attacks disrupted Red Sea shipping in late 2023, the index ticked back up, correctly signaling renewed supply-side inflation pressure. This factor is the bridge between geopolitics (the shock) and inflation (the consequence).

**108. Baltic Dry Index** *(NEW)*
We include this because the BDI is the **purest demand signal in commodity markets.** It measures the cost of shipping bulk commodities (iron ore, coal, grain) and is not subject to speculative trading (you can't go long the BDI for financial gain — it's a real cost of real shipping). The BDI collapsed 94% in 2008 before the recession was officially recognized. It surged in 2021 as China restocked. It is a leading indicator for global trade and industrial production, with a 1-2 month lead time.

**109. Container Shipping Rates** *(NEW)*
We include this because container rates are **distinct from bulk rates (BDI)** and capture consumer goods trade specifically. The Freightos/Drewry indices measure the cost of shipping a 40-foot container from Asia to US/Europe. These rates rose 10x during COVID (from ~$2K to $20K per container), directly adding 1-2% to US goods inflation. The Red Sea disruption in 2024 caused a 4x spike. Container rates feed directly into goods prices with a 2-3 month lag — making them one of the best real-time predictors of near-term goods inflation.

---

### Category 17: Private Credit / Alternatives (2 Factors) — NEW

**Why this category exists:** The financial system has fundamentally changed since the GFC. Bank lending has been constrained by regulation (Basel III, Dodd-Frank), and the gap has been filled by private credit — a $1.5 trillion+ market that has tripled since 2018. This market is opaque (no public pricing), illiquid (no secondary market), and concentrated (top 10 managers control 40%+ of assets). It is also providing the majority of leveraged lending to mid-market companies. If there is a credit cycle turn, private credit is where the stress will be *invisible* until it's too late to react. We include limited visibility here because we believe this is a structural risk building in the system.

**110. Private Credit / CLO Conditions** *(NEW)*
We include this because **private credit is the fastest-growing corner of the financial system and the least monitored.** CLO issuance (the primary funding mechanism) was $180B in 2023. Covenant quality has deteriorated — "covenant-lite" loans are now 90%+ of new issuance, meaning lenders have fewer protections. Default rates in leveraged loans are rising but hidden by PIK (payment-in-kind) and amendment-and-extend strategies that delay recognition. If there is a recession, private credit default rates could spike above 10%, threatening the funds and insurance companies that hold these assets. We monitor via CLO issuance volumes, leveraged loan default rates, and bid-ask spreads in secondary markets — all available via news/RSS analysis.

**111. IPO / Equity Issuance** *(NEW)*
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

We validate the framework against **every major market dislocation from 1960 to 2026** — 42 events across 7 decades. For each event, we trace the causal chain through our 111 factors. If even one link in the chain is missing, the system has a blind spot that will cost us when the next variant of that crisis arrives.

### The 1960s

#### 1966 Credit Crunch
**Chain:** Fiscal Deficit ↑ (Vietnam War + Great Society spending) → CPI ↑ (demand-pull inflation to 3.5%) → Fed Funds Rate ↑ (4.5% → 5.75%) → Lending Standards ↑ (Regulation Q deposit ceilings triggered disintermediation) → FCI ↑ (credit availability collapsed) → Housing Starts ↓ (40% plunge as thrifts lost deposits) → Mortgage Rate ↑ → S&P 500 ↓ (−22% bear market) → Financials ↓ → GDP ↓ (growth slowdown)
**Coverage:** **Full coverage** — captures the fiscal origin, Fed reaction, disintermediation through lending standards and FCI, housing transmission, and equity impact.

#### 1971 Nixon Shock / Bretton Woods Collapse
**Chain:** Fiscal Deficit ↑ (Vietnam twin deficits) → Gold ↑ (foreign central banks demanded conversion, US reserves draining) → DXY ↓ (gold window closed, dollar devalued 8%) → EUR/USD ↑ (European currencies revalued) → USD/JPY ↓ (yen forced to appreciate from 360 → 308) → Breakevens ↑ (inflation expectations unanchored without gold discipline) → Oil ↑ → Copper ↑ → Wheat ↑ (broad commodity surge) → CPI ↑ (import price pass-through, inflation toward 6%) → Rate Expectations ↑
**Coverage:** **Full coverage** — captures the fiscal root cause, gold convertibility break, dollar devaluation across major currencies, commodity repricing, and inflation expectations unanchoring.

### The 1970s

#### 1973 OPEC Oil Embargo
**Chain:** Geopolitical Risk ↑ (Yom Kippur War) → Oil ↑ ($3 → $12, 300% surge) → Natural Gas ↑ → CPI ↑ (headline to 12.3%) → Breakevens ↑ → Consumer Confidence ↓ (gasoline lines, rationing) → GDP ↓ (−3.2%) → Unemployment ↑ (4.6% → 9.0%) → Manufacturing PMI ↓ → S&P 500 ↓ (−48% from Jan 1973 to Oct 1974) → Energy Sector ↑ (windfall profits) → Earnings ↓ (ex-energy collapse) → DXY ↓ → Gold ↑ ($65 → $180)
**Coverage:** **Full coverage** — captures the geopolitical trigger, oil shock, stagflationary divergence, equity sector rotation, dollar weakness, and gold's inflation-hedge bid.

#### 1974-75 Stagflation Recession
**Chain:** Oil ↑ (elevated costs embedded) → CPI ↑ (12.3% peak) → Wage Growth ↑ (union COLA contracts) → Fed Funds Rate ↑ (Burns raised to 13%, then capitulated) → Fed Funds Rate ↓ (premature easing to 5.25%) → Unemployment ↑ (9.0%) → GDP ↓ (−3.2%) → Manufacturing PMI ↓ → Fiscal Deficit ↑ → S&P 500 ↓ (−48%) → PE ↓ (Shiller CAPE compressed to 8.3x) → HY Spread ↑ → Consumer Confidence ↓ → Real Yield ↓ (deeply negative)
**Coverage:** **Full coverage** — captures the wage-price spiral, Fed stop-go policy error, simultaneous inflation-unemployment breakout, and equity valuation compression.

#### 1979 Second Oil Crisis (Iranian Revolution)
**Chain:** Geopolitical Risk ↑ (Iranian Revolution) → Oil ↑ ($14 → $35) → Natural Gas ↑ → CPI ↑ (reaccelerated to 14.8%) → Breakevens ↑ (double-digit expectations entrenched) → Gold ↑ ($225 → $850) → Silver ↑ (Hunt brothers squeeze) → DXY ↓ (dollar confidence crisis) → Consumer Confidence ↓ → GDP ↓ → Unemployment ↑ → S&P 500 ↓ → 10Y Yield ↑ (surged toward 12%) → Real Yield ↓ (still deeply negative)
**Coverage:** **Full coverage** — captures the supply shock, second inflation wave, precious metals mania, dollar confidence crisis, and bond market's failure to outrun inflation.

#### 1979-82 Volcker Shock
**Chain:** Fed Funds Rate ↑ (Volcker raised to 20%) → Rate Expectations ↑ (credible disinflation commitment) → 2Y Yield ↑ (past 16%) → 10Y Yield ↑ (peaked 15.8%) → Mortgage Rate ↑ (30Y fixed hit 18.4%) → Housing Starts ↓ (collapsed 50%) → Lending Standards ↑ → FCI ↑ (tightest since Depression) → GDP ↓ (double-dip recession, −2.7%) → Unemployment ↑ (10.8%) → Manufacturing PMI ↓ → CPI ↓ (14.8% → 3.2%, inflation broken) → DXY ↑ (surged 50%) → EM Sovereign Spread ↑ → EM FX ↓ → Gold ↓ ($850 → $300, inflation hedge unwound) → S&P 500 ↑ (secular bull began August 1982)
**Coverage:** **Full coverage** — captures the rate mechanism, housing/credit transmission, deliberately induced recession, inflation's defeat, dollar surge triggering EM crisis, and the equity inflection.

### The 1980s

#### 1982 Latin American Debt Crisis
**Chain:** Fed Funds Rate ↑ (Volcker rates made dollar debt unserviceable) → DXY ↑ (doubled real burden of dollar-denominated loans) → EM Sovereign Spread ↑ (Mexico declared moratorium August 1982, Brazil and Argentina followed) → EM FX ↓ → EM Equities ↓ → Financials ↓ (Citibank LatAm exposure exceeded total equity) → Regional Banks ↓ → Lending Standards ↑ (banks retrenched from international lending) → HY Spread ↑ → Global Trade Volume ↓ → Fed Funds Rate ↓ (Volcker eased as financial stability risk overtook inflation fight) → Fed Balance Sheet ↑ (emergency liquidity to exposed banks)
**Coverage:** **Full coverage** — captures the Volcker-dollar transmission to EM, sovereign default contagion, US bank exposure, trade contraction, and the Fed's pivot to financial stability.

#### 1985 Plaza Accord
**Chain:** DXY ↓ (coordinated G5 intervention, dollar fell 50% over two years) → EUR/USD ↑ (European competitiveness restored) → USD/JPY ↓ (yen nearly doubled) → BOJ Policy ↓ (discount rate cut to 2.5% to cushion export sector — seeded Japanese bubble) → Japan Equities ↑ → Europe Equities ↑ → Trade Policy ↑ (US bilateral pressure on Japan) → Manufacturing PMI ↑ (US manufacturing recovered) → Gold ↑ (dollar debasement) → EM FX ↑ (dollar weakness relieved EM debt burden) → EM Sovereign Spread ↓ (Brady Plan, restructuring viable with weaker dollar) → S&P 500 ↑
**Coverage:** **Full coverage** — captures coordinated FX intervention, cross-currency transmission, BOJ easing that seeded Japan's bubble, competitiveness rotation, and EM debt relief.

#### 1987 Black Monday (October 19)
**Chain:** S&P 500 ↓ (−22.6% in single session) → VIX ↑ (portfolio insurance delta-hedging created mechanical selling cascade) → Put/Call ↑ → SKEW ↑ (tail risk repriced permanently, "volatility smile" born) → Fund Flows ↓ → Margin Debt ↓ (forced liquidation) → NASDAQ ↓ → Russell 2000 ↓ → Financials ↓ (specialist firms near insolvency) → FCI ↑ → Fed Funds Rate ↓ (Greenspan emergency liquidity, "Fed put" born) → Fed Balance Sheet ↑ → Bank Reserves ↑ → 10Y Yield ↓ (flight to safety) → Gold ↑
**Coverage:** **Full coverage** — captures the portfolio insurance feedback loop, volatility regime change, forced-selling cascade, the birth of the "Greenspan put," and flight-to-safety.

#### 1989 Japanese Asset Bubble Peak
**Chain:** BOJ Policy ↓ (years of 2.5% post-Plaza Accord) → Japan Equities ↑ (Nikkei peaked 38,957; PE above 60x) → Home Prices ↑ (Tokyo land "worth more than California") → Lending Standards ↓ (banks lent against inflated land) → Private Credit ↑ → BOJ Policy ↑ (Mieno raised to 6.0%) → Japan Equities ↓ (began 80% decline over 13 years) → Financials ↓ (bank NPLs exploded) → CRE Stress ↑ (values fell 80%) → Global CB Liquidity ↓ (BOJ shift removed major liquidity source) → EM Equities ↓ (Japanese lending to Asia withdrawn — precursor to 1997)
**Coverage:** **Full coverage** — captures BOJ easing origin, bubble mechanics through lending/credit, tightening trigger, equity/real estate collapse, and withdrawal of Japanese capital from Asia.

#### 1989-91 US Savings & Loan Crisis
**Chain:** Lending Standards ↓ (1982 deregulation let thrifts speculate) → CRE Stress ↑ (speculative development funded by insured deposits) → Private Credit ↑ → Home Prices ↓ (Texas/Southwest collapse with oil bust) → Regional Banks ↓ (~1,000 S&Ls failed) → Financials ↓ → Fiscal Deficit ↑ ($160B taxpayer bailout via RTC) → Lending Standards ↑ (FIRREA imposed strict capital requirements) → FCI ↑ (credit crunch) → HY Spread ↑ (junk bond collapse, Drexel failed) → GDP ↓ (1990-91 recession) → Unemployment ↑ (7.8%) → Housing Starts ↓ → Fed Funds Rate ↓ (9.75% → 3%)
**Coverage:** **Full coverage** — captures deregulation-to-speculation, CRE concentration, mass thrift failure, credit crunch, the junk bond nexus, and Fed easing.

### The 1990s

#### 1992 ERM Crisis / Black Wednesday
**Chain:** ECB Rate (Bundesbank post-reunification tightening forced ERM peers into unsustainable rate defense) → GBP/USD ↓ (Bank of England spent £27B in reserves before capitulating; sterling crashed 15%) → EUR/USD (lira and peseta ejected from ERM) → FX Vol ↑ (peg after peg broke) → Institutional Positioning (Soros's $10B short-sterling bet — macro fund model validated) → Fund Flows (capital flight from weak-ERM currencies into Deutschmark) → Europe Equities (FTSE rallied post-devaluation on competitiveness; continent fell) → EM FX (demonstrated to EM policymakers that pegs invite speculative attack — precursor to 1990s EM crises)
**Coverage:** **Full coverage** — traces Bundesbank intransigence through sterling collapse, macro fund positioning, and the intellectual precursor to Asian/EM currency crises.

#### 1994 Bond Massacre
**Chain:** Fed Funds Rate ↑ (Greenspan's surprise hike February 4, first in 5 years, then six more to 6%) → Rate Expectations (carry trades repriced violently) → 10Y Yield ↑ (5.6% → 8.0%) → 30Y Yield ↑ (duration losses devastated leveraged portfolios) → MOVE ↑ (Orange County's $1.7B loss, P&G's $157M derivatives blowup) → Mortgage Rate ↑ (7% → 9%) → EM Sovereign Spread ↑ (Brady bond spreads widened) → EM FX ↓ (capital reversed from EM carry trades) → Fund Flows ↓ (leveraged bond funds liquidated)
**Coverage:** **Full coverage** — traces the surprise tightening through yield curve repricing, volatility spike, mortgage transmission, and capital flow reversal from EM.

#### 1994 Mexican Peso Crisis (Tequila Crisis)
**Chain:** EM FX ↓ (peso's managed crawl broke; intended 15% devaluation became 50% freefall) → EM Sovereign Spread ↑ (tesobono yields exploded; $29B in dollar-linked debt unserviceable) → DXY ↑ (capital fled to US) → EM Equities ↓ (Bolsa −43% in dollar terms; Argentina −28% on contagion) → Fund Flows ↓ ($10B+ EM outflows) → FCI ↑ (Latin American interbank rates spiked) → US Political Risk (Clinton's $50B bailout bypassed Congress; shaped future bailout reluctance) → Lending Standards ↑ (US banks tightened EM credit)
**Coverage:** **Full coverage** — traces peso collapse through sovereign distress, dollar strength, equity contagion, capital flight, and the politically contentious bailout.

#### 1997 Asian Financial Crisis
**Chain:** EM FX ↓ (Thai baht floated July 2 after $23B defending peg; fell 50%; contagion to won, rupiah, ringgit, peso) → EM Sovereign Spread ↑ (Korea spread hit 900bp) → EM Equities ↓ (MSCI EM −58%; Jakarta −65%) → FX Vol ↑ → Fund Flows ↓ ($100B+ in outflows) → DXY ↑ (global flight to safety) → Copper ↓ (−30%, Asian demand collapsed) → Oil ↓ ($26 → $11) → Global Trade Volume ↓ (Asian trade finance froze) → Japan Equities ↓ (banks faced Asian loan losses; Yamaichi collapsed) → China PMI ↓ (regional partners contracted) → Lending Standards ↑ (global banks retrenched from EM) → HY Spread ↑ (+150bp on contagion) → VIX ↑ (>35 on Hong Kong contagion)
**Coverage:** **Full coverage** — traces the baht devaluation through regional contagion, capital reversal, commodity demand destruction, Japanese bank stress, Chinese spillover, and US credit/equity impact.

#### 1998 Russian Default + LTCM Collapse
**Chain:** EM Sovereign Spread ↑ (Russia defaulted on GKOs August 17; moratorium on $40B foreign obligations) → EM FX ↓ (ruble 6 → 21; Brazilian real under severe pressure) → EM Equities ↓ (Russian market lost 93%) → TED Spread ↑ (tripled as interbank trust evaporated) → CDS ↑ (LTCM's $1.25T derivatives book threatened counterparty cascade) → Institutional Positioning (LTCM's convergence trades all diverged as correlations went to 1) → HY Spread ↑ (+300bp; new issuance froze) → IG Spread ↑ (doubled; forced selling from deleveraging) → 10Y Yield ↓ (on-the-run plunged to 4.16% on flight-to-quality) → Gold ↑ (initially, then sold for liquidity) → VIX ↑ (>45 in October) → Lending Standards ↑ (sharpest tightening since 1990-91) → FCI ↑ (+200bp equivalent) → Fund Flows ↓ (mass redemptions; LTCM's 14 banks organized $3.6B recap) → S&P 500 ↓ (−22% before Fed's three emergency cuts restored confidence)
**Coverage:** **Full coverage** — traces Russia's default through LTCM's near-collapse, flight-to-quality, interbank/credit seizure, forced deleveraging, and the Fed's emergency response.

#### 1999-2000 Dot-com Bubble Peak
**Chain:** NASDAQ ↑ (+86% in 1999 to peak 5,048 on March 10, 2000) → Tech Sector (internet stocks at infinite PE) → PE ↑ (Shiller CAPE 44x; NASDAQ median PE >100x) → Semiconductors ↑ (SOX tripled) → Retail Sentiment ↑ (day-trading mainstream; E*Trade accounts +300%) → Margin Debt ↑ ($278B, +75% YoY) → IPO Issuance ↑ (486 IPOs in 1999; 71% average first-day return) → Fund Flows ↑ ($309B equity inflows) → ERP ↓ (compressed to zero — no risk compensation demanded) → S&P 500 ↑ (broad market followed tech) → VIX ↓ (suppressed at 20-23 despite extreme speculation) → Fed Funds Rate ↑ (Greenspan raised six times to 6.5%)
**Coverage:** **Full coverage** — traces the speculative mania through retail participation, leverage, IPO frenzy, risk premium collapse, and belated Fed tightening.

### The 2000s

#### 2000-02 Dot-com Bust
**Chain:** NASDAQ ↓ (−78% from peak) → Tech Sector ↓ → Semiconductors ↓ → PE ↓ → Earnings ↓ → Revenue ↓ → IPO Issuance ↓ (market froze) → Margin Debt ↓ (forced liquidation) → VIX ↑ → S&P 500 ↓ → Russell 2000 ↓ → Fed Funds Rate ↓ (6.5% → 1.0%) → Unemployment ↑ (6.3%) → Consumer Confidence ↓ → GDP ↓ (recession)
**Coverage:** **Full coverage** — speculative tech valuations collapsed as earnings failed to materialize, freezing IPO issuance and triggering margin liquidation, forcing the Fed to cut 550bp as unemployment rose.

#### 2001 September 11 Attacks
**Chain:** Geopolitical Risk ↑ (permanent repricing) → VIX ↑ (>40) → S&P 500 ↓ (−12% on reopening) → Earnings ↓ → HY Spread ↑ → IG Spread ↑ → Fund Flows ↓ → Gold ↑ (safe haven) → 10Y Yield ↓ (flight to quality) → DXY ↑ → Oil ↑ (supply fear, then demand destruction) → Fed Funds Rate ↓ (emergency −175bp by year-end) → Consumer Confidence ↓
**Coverage:** **Full coverage** — captures the permanent geopolitical risk repricing, flight-to-safety, credit spread widening, and the Fed's emergency response.

#### 2007-08 Subprime Crisis → Global Financial Crisis
**Chain:** Mortgage Rate ↑ → Home Prices ↓ → Housing Starts ↓ → CRE Stress ↑ → Private Credit ↓ (structured credit collapsed) → Lending Standards ↑ → HY Spread ↑ → IG Spread ↑ → TED Spread ↑ (+300bp, interbank trust collapsed) → CP Spread ↑ (commercial paper froze) → MMF Flows (Reserve Primary Fund "broke the buck") → Bank Reserves ↓ → Repo/SOFR ↑ (funding markets seized) → FCI ↑↑ → Financials ↓ → Regional Banks ↓ → S&P 500 ↓ (−57%) → VIX ↑ (>80) → Margin Debt ↓ → Fund Flows ↓ → Earnings ↓ → Unemployment ↑ (10%) → Consumer Confidence ↓ → GDP ↓ (−4.3%) → EM Sovereign Spread ↑ → EM FX ↓ → EM Equities ↓ → DXY ↑ (dollar funding crisis) → Gold ↑ → Fed Funds Rate ↓ (to 0%) → Fed Balance Sheet ↑ ($4T QE) → Global CB Liquidity ↑ → Fiscal Deficit ↑ ($1.4T) → Debt/GDP ↑ → Govt Spending ↑ (ARRA stimulus)
**Coverage:** **Full coverage** — the most comprehensive chain in our framework: subprime defaults through structured credit collapse, interbank trust failure, commercial paper/money market freeze, Lehman bankruptcy, global dollar funding crisis, EM contagion, coordinated central bank QE, and massive fiscal expansion.

### The 2010s

#### 2010 Flash Crash (May 6) *(NEW)*
**Chain:** Institutional Positioning (Waddell & Reed's $4.1B E-mini sell algorithm triggered in already nervous market) → S&P 500 ↓ (−9.2% in 36 minutes; individual stocks traded at $0.01 and $100,000) → VIX ↑ (25→40 intraday) → ETF Flows ↓ (ETF arbitrage mechanisms broke; 65% of cancelled trades were ETFs) → Margin Debt ↓ (real-time margin calls) → Retail Sentiment ↓ (retail trust in market structure destroyed) → Fund Flows ↓ (equity fund outflows accelerated for months) → Financial Conditions ↑ (brief liquidity vacuum) → S&P 500 ↑ (recovery within 36 minutes, but structural damage permanent)
**Coverage:** **Full coverage** — captures the algorithmic cascade, ETF structural breakdown, and the revelation that modern market microstructure can produce discontinuous price moves. Led directly to SEC circuit breakers and Reg SCI.

#### 2011 European Sovereign Debt Crisis
**Chain:** EU Periphery Spreads ↑ (Greece 10Y hit 35%; Italy, Spain, Portugal followed; contagion turned existential — would the Euro survive?) → CDS ↑ (sovereign CDS repriced all European bank exposure; Greek PSI imposed 53.5% haircut on private bondholders) → Financials ↓ (European banks held €hundreds of billions in peripheral bonds; US money market funds had $1T+ in European bank CP/CD exposure) → ECB Rate ↑ (Trichet's catastrophic error: hiked April and July 2011 into a recession, then reversed) → EUR/USD ↓ → IG Credit Spread ↑ (European corporate credit froze) → HY Credit Spread ↑ → FCI ↑ → Lending Standards ↑ (European bank deleveraging drained credit) → VIX ↑ (>45 in August) → S&P 500 ↓ (−19% in weeks) → Gold ↑ ($1,900 record) → 10Y Yield ↓ (flight to US Treasuries) → EM Sovereign Spread ↑ → Fund Flows ↓ (EM outflows on global risk-off) → ECB Rate ↓ (Draghi cut rates, launched LTRO, then "whatever it takes" July 2012)
**Coverage:** **Full coverage** — traces peripheral contagion through ECB policy error, bank deleveraging, cross-Atlantic money market exposure, credit freeze, and the eventual "whatever it takes" resolution that saved the Euro.

#### 2013 Taper Tantrum
**Chain:** Rate Expectations ↑ (Bernanke's May 22 testimony: "we could take a step down in our pace of purchases" — markets went berserk) → 10Y Yield ↑ (1.6%→3.0% in 4 months) → Real Yield ↑ (+100bp) → MOVE ↑ (rate vol spiked) → Mortgage Rate ↑ (3.4%→4.6%; housing recovery stalled) → DXY ↑ → EM FX ↓ (India rupee −20%, Brazil real −15%, Turkey lira −15%, South Africa rand −20%) → EM Sovereign Spread ↑ (+200bp; "Fragile Five" coined) → EM Equities ↓ (MSCI EM −15%) → Fund Flows ↓ ($50B+ EM bond outflows) → Copper ↓ → Gold ↓ (−25%; worst year since 1981 as real yields surged) → Capital flight → DXY ↑ (self-reinforcing feedback loop)
**Coverage:** **Full coverage** — traces the forward guidance shock through yield surge, EM contagion via the dollar wrecking ball, and the first demonstration that QE exit expectations alone could destabilize global markets.

#### 2014-15 Oil Price Collapse
**Chain:** Oil ↓ ($115 → $26, OPEC price war) → Energy Sector ↓ → Earnings ↓ → Revenue ↓ → HY Spread ↑ (energy is largest HY sector; spreads hit 800bp) → Russell 2000 ↓ → EM Sovereign Spread ↑ (Russia, Nigeria, Venezuela) → EM FX ↓ → EM Equities ↓ → Sanctions (compounded Russia's oil stress) → CPI ↓ → Breakevens ↓ → Rate Expectations ↓ (Fed delayed tightening until Dec 2015) → DXY ↑
**Coverage:** **Full coverage** — traces OPEC's market share war through energy HY blowout, EM oil-exporter devastation, deflationary impulse, and the Fed's delayed tightening.

#### 2015 Swiss Franc Peg Removal (January 15) *(NEW)*
**Chain:** ECB Rate ↓ (Draghi signaled imminent QE → SNB concluded EUR/CHF floor was unsustainable) → FX Volatility ↑↑ (EUR/CHF moved 30% in seconds — most violent G10 FX move in modern history; no liquidity between 1.20 and 0.85) → Financials ↓ (FXCM received $300M emergency bailout, Alpari UK insolvent, Citi lost $150M+) → EM FX ↓ (repriced all managed exchange rate regimes) → Institutional Positioning (carry traders crushed; short-CHF positions wiped out) → Gold ↑ (safe-haven bid) → VIX ↑ → Margin Debt ↓ (forced liquidation across FX brokerages)
**Coverage:** **Full coverage** — most important FX regime break since 1992 ERM. Proved central bank credibility can evaporate instantaneously and FX moves can be discontinuous.

#### 2015 China Devaluation Scare
**Chain:** PBOC Policy shift (August 11 surprise devaluation — largest in two decades; interpreted as competitive devaluation) → USD/CNY ↑ (capital outflows accelerated to $100B/month) → China Credit Impulse ↓ (PBOC tightened to defend currency) → China Equities ↓ (Shanghai −43% from June peak; circuit breakers introduced Jan 2016, triggered immediately, abandoned after 4 days) → EM Equities ↓ (−25%) → EM FX ↓ (competitive devaluation fears) → Copper ↓ (−25%) → Iron Ore ↓ → Baltic Dry Index ↓ (approaching all-time lows) → VIX ↑ (>40 on August 24 "Black Monday") → S&P 500 ↓ (−12% in 6 sessions) → Global Trade Volume ↓ → Rate Expectations ↓ (Fed delayed September 2015 hike)
**Coverage:** **Full coverage** — traces PBOC devaluation shock through capital flight, equity crash, commodity demand destruction, and the Fed's forced delay of rate normalization.

#### 2018 Volmageddon (February 5)
**Chain:** VIX ↑ (13 → 50 intraday) → SKEW (prior warnings materialized) → Put/Call ↑ → Institutional Positioning (short-vol ETFs XIV/SVXY destroyed; forced VIX futures buying by issuers created reflexive feedback) → ETF Flows ↓ → Margin Debt ↓ → Fund Flows ↓ → S&P 500 ↓ (−4%) → Retail Sentiment ↓ → FCI ↑
**Coverage:** **Full coverage** — captures the short-vol blowup, reflexive feedback loop, and the revelation that volatility is a cause, not just a symptom.

#### 2018 EM Crisis (Turkey / Argentina)
**Chain:** US Political Risk → Sanctions (on Turkey) → EM FX ↓ (lira −45%; peso collapsed) → FX Vol ↑ → EM Sovereign Spread ↑ → EM Equities ↓ → Fund Flows ↓ ($30B EM outflows) → DXY ↑ → Fed Funds Rate ↑ (continued tightening to 2.5% — background gravity) → Copper ↓ → Oil ↓ → Gold ↑ → VIX ↑
**Coverage:** **Full coverage** — traces US sanctions through EM FX contagion, fund flow reversal, and the Fed's tightening as background amplifier.

### The 2020s

#### 2020 COVID Pandemic
**Chain (crash — fastest bear market in history, 23 trading days):** Geopolitical Risk ↑ (pandemic declaration March 11) → Supply Chain Pressure ↑↑ (global shutdown) → VIX ↑ (>82, exceeding GFC peak) → Margin Debt ↓ (margin calls cascaded across all asset classes) → S&P 500 ↓ (−34%) → HY Spread ↑ (1,100bp) → IG Spread ↑ (400bp) → TED Spread ↑ → CP Spread ↑ (commercial paper seized; corporates drew $200B+ on revolvers in one week) → MMF Flows ↓ (institutional prime funds saw $120B outflows) → Oil ↓ (−$37.63 on April 20 — negative prices for first time in history) → EM FX ↓ → EM Sovereign Spread ↑ → 10Y Yield ↓ (0.31%, all-time low) → Bitcoin ↓ (−50% in 48 hours)
**Chain (recovery):** Fed Funds Rate ↓ (emergency −150bp in 11 days to 0%) → Fed Balance Sheet ↑ ($4T→$9T; Fed bought corporate bonds for first time) → Global CB Liquidity ↑↑ → Fiscal Deficit ↑↑ ($3.1T; CARES Act, PPP — largest peacetime fiscal expansion ever) → Govt Spending ↑ → PBOC Policy ↓ → China Credit Impulse ↑ → Copper ↑ (+100%) → NASDAQ ↑ (+44% in 2020; tech was the pandemic winner) → Bitcoin ↑ (+300%) → Home Prices ↑ (+20%; mortgage rates at 2.65%) → Retail Sentiment ↑ (stimulus checks + boredom + zero-commission trading = meme stock era)
**Coverage:** **Full coverage** — most comprehensive crisis-and-recovery chain: pandemic shock, fastest bear market, oil going negative, Fed buying corporate bonds, $3T fiscal expansion, and the everything-rally that seeded 2022 inflation.

#### 2021 GameStop / Meme Stock Squeeze (January) *(NEW)*
**Chain:** Retail Sentiment ↑↑ (WallStreetBets coordinated buying of heavily-shorted stocks; GME $17→$483 in 16 days) → Margin Debt ↑ (retail options activity at all-time highs) → Institutional Positioning (Melvin Capital lost 53% in January; short squeeze forced covering of $25B+ in short positions) → VIX ↑ (21→37) → Russell 2000 ↑ (meme stocks were small-caps) → Fund Flows ↑ → ETF Flows ↑ → Financial Conditions (Robinhood halted GME purchases — broker liquidity constraints exposed; Congressional hearings followed) → US Political Risk ↑ (payment for order flow scrutiny, market structure reform debate) → Bitcoin ↑ (retail enthusiasm spillover)
**Coverage:** **Full coverage** — captures retail-vs-institutional dynamic, short squeeze mechanics, broker liquidity constraints, and the political/regulatory aftermath.

#### 2021 Archegos Collapse (March) *(NEW)*
**Chain:** Margin Debt ↑↑ (Archegos had $20B+ in leveraged total return swap exposure across 6 prime brokers) → Institutional Positioning (ViacomCBS secondary triggered selloff; Archegos couldn't meet margin calls) → Financials ↓ (Credit Suisse lost $5.5B, Nomura $3B; CS's risk management failure contributed to its eventual collapse 2 years later) → Private Credit ↑ (total return swap opacity exposed; $50B+ in hidden leverage) → CDS ↑ (Credit Suisse CDS widened significantly) → IG Credit Spread ↑ (brief widening) → Lending Standards ↑ (prime brokers tightened swap margin requirements)
**Coverage:** **Full coverage** — exposed shadow leverage in total return swaps where a single family office accumulated $20B+ without public disclosure. Archegos loss was a direct contributor to Credit Suisse's 2023 collapse.

#### 2022 Inflation / Rate Shock
**Chain:** Supply Chain Pressure ↑ (COVID aftershock + stimulus demand) + Oil ↑ ($65→$120) + Wage Growth ↑ (5%+, labor shortage) → CPI ↑↑ (9.1% June 2022 — highest since 1981) → Fed Funds Rate ↑↑ (0%→5.25% in 16 months; four consecutive 75bp hikes) → Rate Expectations ↑ (repriced from "transitory" to "structural") → Real Yield ↑ (−1.0%→+2.5%) → 10Y Yield ↑ (1.5%→4.2%) → Mortgage Rate ↑ (2.65%→7.08%) → Housing Starts ↓ (−25%) → Home Prices ↓ → NASDAQ ↓ (−33%) → Bitcoin ↓ (−75%) → S&P 500 ↓ (−25%) → PE Valuations ↓ (CAPE 38x→28x) → EM FX ↓ (DXY hit 20-year high at 114) → EM Sovereign Spread ↑ → Russell 2000 ↓ (−28%) → Consumer Confidence ↓ → Fund Flows ↓ (record bond fund outflows)
**Coverage:** **Full coverage** — traces triple inflation drivers (supply chains, energy, wages), fastest tightening since Volcker, the real yield repricing that unified equity/crypto/housing selloffs as a single trade, and dollar wrecking ball EM transmission.

#### 2022 Russia-Ukraine War
**Chain:** Geopolitical Risk ↑ (largest European land war since 1945) → Oil ↑ ($90→$130) → Natural Gas ↑ (European TTF 10x to €340/MWh; Nord Stream sabotaged) → Wheat ↑ (+60%; Russia-Ukraine supply 30% of global exports) → EU HICP ↑ (10.6% — eurozone record; energy component +40%) → ECB Rate ↑ (0%→4%; fastest ECB tightening ever) → EUR/USD ↓ (below parity, first since 2002) → Europe Equities ↓ (German industrials hammered) → Sanctions ↑ (most comprehensive since WWII: Russian central bank reserves frozen, SWIFT disconnection, oil price cap) → Container Shipping ↑ (global energy trade rerouted) → Supply Chain Pressure ↑ → Energy Sector ↑ (+65%; best sector while everything else fell) → Gold ↑ ($2,070; central bank buying surged to record) → EM Sovereign Spread ↑ (food-importing nations: Egypt, Sri Lanka faced instability) → EM FX ↓ → Global Trade Volume ↓
**Coverage:** **Full coverage** — traces the largest geopolitical shock since 9/11 through commodity spikes, European energy crisis, ECB forced tightening, sanctions restructuring, and EM food security contagion.

#### 2022 UK Gilt Crisis (Truss Mini-Budget)
**Chain:** Fiscal Deficit ↑ (unfunded £45B tax cuts) → Debt/GDP ↑ (fiscal credibility destroyed) → GBP/USD ↓ (−10%) → 30Y Yield ↑ (+150bp in days; LDI pension funds faced margin calls) → MOVE ↑ → FX Vol ↑ → Institutional Positioning (£1.5T in leveraged gilt exposure forced to liquidate) → Fund Flows ↓ → FCI ↑ → Lending Standards ↑ → DXY ↑ → US Political Risk (fiscal credibility contagion fear) → Gold ↑
**Coverage:** **Full coverage** — traces the unfunded fiscal shock through sterling crash, LDI pension margin calls, forced gilt selling, and the global contagion fear about developed-market fiscal credibility.

#### 2022 Luna/Terra + FTX Collapse (May-November) *(NEW)*
**Chain:** Bitcoin ↓ (falling with broader risk assets on rate hikes) → Luna/UST de-peg ($40B evaporated in 72 hours; algorithmic stablecoin death spiral) → Retail Sentiment ↓↓ → Margin Debt ↓ (Three Arrows Capital — $10B hedge fund — insolvent within weeks) → Private Credit ↑ (crypto lenders collapsed: Celsius, Voyager, BlockFi halted withdrawals) → Bitcoin ↓ further ($30K→$16K) → FTX collapse (November: $32B exchange revealed as fraud) → Regional Banks ↓ (Silvergate and Signature Bank failed early 2023 — direct precursor to SVB) → MMF Flows ↑ (crypto deposits fled) → Lending Standards ↑ (banks pulled back from crypto lending) → CDS ↑ (bank CDS widened)
**Coverage:** **Full coverage** — traces crypto contagion from stablecoin failure through leveraged lender cascade, exchange fraud, and the banking connection (Silvergate/Signature) that made crypto stress a traditional finance problem.

#### 2023 SVB Crisis
**Chain:** Real Yield ↑ (2022 rate shock left SVB holding $21B in HTM losses against $16B equity — technically insolvent mark-to-market) → MOVE ↑ → Regional Banks ↓ (SVB failed March 10, Signature March 12, First Republic May 1; KRE −35%) → MMF Flows ↑↑ ($500B deposit flight in one week — largest in history; SVB lost $42B in a single day — first social-media bank run) → Bank Reserves ↓ (Fed created emergency BTFP) → Lending Standards ↑↑ (SLOOS at GFC levels) → CRE Stress ↑ (regional banks hold 70% of CRE loans; $1.5T in maturing CRE debt at risk) → HY Credit Spread ↑ → FCI ↑ → CDS ↑ (Credit Suisse CDS exploded; UBS forced rescue March 19) → Rate Expectations ↓ (market priced 3+ cuts) → VIX ↑ → Gold ↑ ($1,800→$2,000+)
**Coverage:** **Full coverage** — traces rate-induced bond losses through first social-media bank run, record deposit flight, regional bank lending contraction, CRE stress, and Credit Suisse collateral kill.

#### 2024 AI Boom
**Chain:** Semiconductors ↑↑ (NVIDIA revenue $27B→$61B in one year) → Tech Sector ↑ (+50% from Oct 2023 lows; "Magnificent 7" concentration unprecedented) → NASDAQ ↑ (+43% in 2023) → S&P 500 ↑ (top 10 = 35% of index, highest since 1970s) → Earnings ↑ (Mag 7 earnings +60%; remaining 493 flat) → PE Valuations ↑ (22x forward) → Equity Risk Premium ↓ (compressed to near zero — stocks offered no excess over risk-free bonds since 2007) → Productivity debate (does AI raise productivity 1.5%→3.0%? If yes, valuations justified; if no, dot-com echo) → Buybacks ↑ ($1T+, record) → ETF Flows ↑ (passive inflows mechanically concentrated into largest stocks) → Russell 2000 ↓ (relative; lagged S&P by 20%+) → Energy Sector ↑ (AI data center power demand → uranium ↑, natural gas ↑)
**Coverage:** **Full coverage** — traces AI capex boom through semiconductor demand, mega-cap concentration, risk premium compression, and divergence between AI winners and the broader economy.

#### 2024 Yen Carry Trade Unwind (August 5)
**Chain:** BOJ Policy ↑ (rate hike to 0.25% July 31; hawkish forward guidance) → USD/JPY ↓ (161→142 in 3 weeks; yen +12%) → FX Vol ↑↑ (1-week USD/JPY implied vol hit 20%, 4x normal) → Institutional Positioning (extreme JPY shorts at multi-year highs; carry trade estimated $500B-$1T) → Japan Equities ↓ (Nikkei −12.4% August 5, worst since 1987) → VIX ↑ (15→65 intraday, third-largest spike ever) → S&P 500 ↓ (−3% August 5; −6% from July high) → NASDAQ ↓ (−3.4%) → EM FX ↓ (carry trade unwound from EM positions) → Margin Debt ↓ (forced liquidation) → Gold ↑ (safe-haven rotation) → 10Y Yield ↓ (flight to quality) → DXY ↓
**Coverage:** **Full coverage** — most violent single-day equity event of 2024. Proved BOJ normalization cascades through carry trade unwinds to crash New York equities within hours.

#### 2025 Tariff Escalation
**Chain:** Trade Policy ↑↑ (25% on most imports, 60%+ on Chinese goods; largest escalation since Smoot-Hawley) → Supply Chain Pressure ↑ (manufacturers front-loaded imports) → Container Shipping ↑ → CPI ↑ (tariff pass-through +0.5-1.5% core PCE) → Manufacturing PMI ↓ (input cost pressure) → China Equities ↓ (−20%+; trade decoupling priced in) → USD/CNY ↑ (PBOC allowed depreciation to offset tariffs) → EM FX ↓ → EM Equities ↓ → Copper ↓ → Iron Ore ↓ → Global Trade Volume ↓ (WTO projected −5%) → Baltic Dry Index ↓ → Consumer Confidence ↓ → Rate Expectations ± (stagflation dilemma: tariffs inflationary but growth-destructive) → Europe Equities ↓ (exporters crushed by retaliatory tariffs) → Soybeans ↓ (Chinese retaliation on US agriculture)
**Coverage:** **Full coverage** — traces most aggressive protectionism since 1930s through supply chain disruption, inflationary pass-through, China/EM transmission, global trade contraction, and Fed's stagflation dilemma.

#### 2026 US-Iran Conflict / Oil Shock
**Chain:** Geopolitical Risk ↑ → Sanctions ↑ → Oil ↑ (>$110) → Natural Gas ↑ → Energy Sector ↑ → CPI ↑ → Breakevens ↑ → 10Y Yield ↑ → Real Yield ↑ → DXY ↑ → Gold ↓ (yield suppression: bonds at 4.5% vs gold's 0%) → EM Sovereign Spread ↑ → EM FX ↓ → VIX ↑
**Coverage:** **Full coverage** — the oil-driven inflation pushes yields and the dollar higher, mechanically suppressing gold despite peak geopolitical risk. The yield suppression channel dominates the safe-haven channel.

#### Crypto Cycles (2017-present)
**Chain (bull):** Global CB Liquidity ↑ → Real Yield ↓ → Bitcoin ↑ → Retail Sentiment ↑↑ (FOMO, social media amplification) → Margin Debt ↑ (crypto leverage via exchanges, DeFi) → ETF Flows ↑ (spot Bitcoin ETF January 2024 brought $50B+ institutional flows) → NASDAQ ↑ (correlation: crypto tracks tech in risk-on) → Private Credit ↑ (crypto lending platforms expand)
**Chain (bust):** Real Yield ↑ (or idiosyncratic shock: Luna, FTX) → Bitcoin ↓ → Margin Debt ↓↓ (cascading liquidations) → Retail Sentiment ↓ → Private Credit ↓ (Celsius, BlockFi, Genesis failed) → Regional Banks ↓ (Silvergate, Signature — crypto deposit concentration) → ETF Flows ↓ → VIX ↑ (if contagion sufficient)
**Coverage:** **Full coverage** — complete bull-and-bust chain including institutional adoption (ETFs), banking connection (crypto banks), and private credit contagion (lending platform failures).

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

### Chain 10: Geopolitical Oil Shock → Yield Suppression of Gold
```
Geopolitical Risk ↑ → Brent Crude Oil ↑ → CPI ↑ + Breakeven Inflation ↑
                                        → 10Y Treasury Yield ↑ (inflation premium)
                                        → Real Yield ↑ (nominal yield rises faster than breakevens)
                                        → DXY ↑ (rate differential attracts capital)
                                        → Gold ↓ (yield suppression — bonds at 4.5% vs gold's 0%)
```
This is the chain playing out in March 2026 following the US-Iran conflict. Gold does not behave as a simple safe haven when oil-driven inflation pushes bond yields higher. The key mechanism: bonds paying 4.5% with full government backing are the most powerful mechanical suppressor of gold prices. Precious metals trade inversely to oil in the short term through this yield channel.

### Chain 11: The Fiscal Trap → Forced Rate Cuts → Gold Reversal
```
Phase 1 — The Doom Loop:
US Fiscal Deficit ↑ → Treasury Issuance ↑ → 10Y Yield ↑ → Debt Service Cost ↑ → Fiscal Deficit ↑↑
                   → Debt/GDP ↑ → Term Premium ↑ → 10Y Yield ↑↑ (amplifying)

Phase 2 — The Mathematical Trap:
  Path A: Fed raises rates to fight oil-driven inflation
    → Debt service becomes unsustainable ($1T+ annual interest at 4-5% on $9.2T rolling over)
    → Sovereign credibility questioned → further yield rise → even larger deficit
  Path B: Fed cuts rates to manage debt burden
    → Inflation expectations reignite → breakevens surge → gold bid
    → Dollar weakens → commodity prices rise → more inflation

Phase 3 — The Forced Resolution:
Market concludes rates MUST come down — not because inflation is beaten,
but because the debt load leaves no choice:
  Debt/GDP → Rate Expectations ↓ (fiscal dominance priced in)
  → Fed Funds Rate ↓ (forced easing)
    → 10Y Yield ↓ (despite elevated oil)
    → DXY ↓ (rate differential narrows)
    → Gold ↑↑ (responding to BOTH persistent inflation AND monetary loosening the debt forced)
```
This is the chain professional macro traders are positioning for. The yield suppression mechanism from Chain 10 has a finite lifespan — it persists only as long as the market believes the Fed can raise rates. The moment fiscal dominance is priced in, the suppression reverses: yields fall not because inflation is beaten but because the government cannot afford higher rates. Gold then rises from both channels simultaneously — inflation hedge AND monetary debasement hedge.

### Chain 12: BOJ Normalization → Yen Carry Unwind → Global Vol
```
BOJ tightens (rate hike or YCC exit) → USD/JPY ↓ (yen strengthens rapidly)
                                     → FX Volatility ↑
                                     → VIX ↑ (Aug 5, 2024: VIX 15 → 65 intraday)
                                     → Forced selling of US equities/EM funded by yen carry
                                     → S&P 500 ↓, EM Equities ↓, EM FX ↓
                                     → Margin calls → More forced selling
                                     → Gold ↑ (safe-haven rotation)
                                     → DXY ↓ (carry trade unwind reduces USD demand)
```
This chain was proven empirically on August 5, 2024 — the most violent single-day equity move of that year, triggered entirely by a BOJ rate hike and the resulting yen carry trade unwind. It demonstrates that a central bank policy shift in Tokyo can crash equity markets in New York within hours.

---

## Dominant Transmission Chains

Not all paths through the graph are equally important. With 111 nodes and 1,080+ edges, there are millions of possible multi-hop chains — but signal attenuates with each hop (the system applies 30% decay per hop), meaning a 4-hop chain retains ~24% of the original signal and a 6-hop chain retains ~12%. In practice, **3-4 hops is the effective horizon for actionable signals**; longer chains matter only for structural/secular analysis.

The following 25 chains are ranked by **historical explanatory power** — how frequently each chain has been the dominant transmission mechanism in major market dislocations. Each includes an end-to-end lag profile.

### Tier 1: Primary Transmission Chains (fire in every cycle)

**1. The Rate Transmission Chain** — *End-to-end lag: 12-18 months*
```
Fed Funds Rate → [days] → 10Y Yield → [days-weeks] → Mortgage Rate → [weeks-months] → Housing Starts → [months] → GDP Growth
```
The textbook monetary policy mechanism. Active in every tightening cycle. Responsible for the 2022-23 housing freeze.

**2. The Inflation → Policy → Discount Rate Chain** — *End-to-end lag: 3-12 months*
```
CPI → [weeks-months] → Fed Funds Rate → [days] → Real Yield → [hours-days] → NASDAQ + Bitcoin + Gold (all repriced)
```
The unified 2022 trade. Everything long-duration fell together because it was all one chain.

**3. The Dollar Wrecking Ball** — *End-to-end lag: days-weeks, self-reinforcing*
```
Fed tightening → [days] → DXY ↑ → [hours-days] → EM FX ↓ → [hours-days] → EM Sovereign Spread ↑ → [days] → Capital flight → DXY ↑ (feedback)
```
Why EM crises are self-reinforcing. Active in 1982, 1994, 1997, 2013, 2018, 2022.

**4. The Volatility Cascade** — *End-to-end lag: hours-days*
```
Shock → [hours] → VIX ↑ → [hours] → Vol-targeting deleveraging → Forced equity selling → [hours] → S&P ↓ → VIX ↑ (feedback)
```
The mechanism that turns corrections into crashes. Feb 2018, Aug 2024, every flash crash.

**5. The Financial Plumbing Chain** — *End-to-end lag: hours-days*
```
Bank Reserves ↓ → [hours] → Repo/SOFR ↑ → [hours] → TED Spread ↑ → [hours-days] → FCI ↑ → [days] → Equities ↓
```
When plumbing breaks, everything breaks. 2008, 2019 repo, 2020 COVID, 2023 SVB.

### Tier 2: High-Frequency Chains (fire in most cycles)

**6. The Credit Accelerator** — *End-to-end lag: months, self-reinforcing in crisis*
```
HY Spread ↑ → [days] → FCI ↑ → [weeks-months] → GDP ↓ → [months] → Default Risk ↑ → HY Spread ↑ (feedback)
```
The financial accelerator. Amplifies in crises, dampens in expansions.

**7. The Fiscal Doom Loop** — *End-to-end lag: quarters, self-reinforcing*
```
Fiscal Deficit ↑ → [weeks] → Treasury Issuance ↑ → [days] → 10Y Yield ↑ → [quarters] → Debt Service ↑ → Fiscal Deficit ↑ (feedback)
```
The structural risk of the 2020s decade. Drove the 2023 bond selloff.

**8. The China → Global Growth Chain** — *End-to-end lag: 6-9 months*
```
PBOC Policy → [weeks-months] → China Credit Impulse → [months] → China Property + China PMI → [days-weeks] → Iron Ore + Copper → [weeks] → Global Trade Volume
```
China credit impulse today predicts global industrial production 6 months from now.

**9. The Geopolitical → Inflation Chain** — *End-to-end lag: weeks-months*
```
Geopolitical Risk → [hours] → Oil ↑ + Natural Gas ↑ → [weeks-months] → CPI ↑ → [weeks-months] → Fed Funds Rate response
```
Russia-Ukraine, Red Sea, Iran — all follow this pattern.

**10. The Housing Wealth Effect Chain** — *End-to-end lag: months-quarters*
```
Mortgage Rate → [months] → Home Prices → [weeks] → Consumer Confidence → [months] → GDP Growth
       ↓                        ↓
  Home Prices → [months] → CPI (shelter, 40% of CPI) → Fed Funds Rate
```
Housing affects the economy through wealth effects AND inflation simultaneously.

### Tier 3: Crisis-Specific Chains (fire in stress environments)

**11. The EM Contagion Doom Loop** — *End-to-end lag: days-weeks, self-reinforcing*
```
EM FX ↓ → [hours-days] → EM Sovereign Spread ↑ → [days] → Fund Flows ↓ → [days] → EM FX ↓ (feedback)
```

**12. The Bank Run Chain** — *End-to-end lag: hours-days*
```
Regional Banks ↓ → [hours-days] → MMF Flows ↑ (deposit flight) → [days] → Bank Reserves ↓ → [weeks] → Lending Standards ↑ → [months] → GDP ↓
```
SVB 2023. The social-media-accelerated variant executes in hours.

**13. The Carry Trade Unwind Chain** — *End-to-end lag: hours*
```
BOJ tightens → [hours] → USD/JPY ↓ → [hours] → FX Vol ↑ → [hours] → VIX ↑ → [hours] → Global equity selling
```
August 5, 2024. Transmission from Tokyo to New York in a single trading session.

**14. The Oil → Yield Suppression → Gold Chain** — *End-to-end lag: days-weeks*
```
Oil ↑ → [hours-days] → CPI ↑ → [days] → 10Y Yield ↑ → [hours-days] → Real Yield ↑ → [hours-days] → Gold ↓
```
Counter-intuitive: geopolitical risk suppresses gold through yields. March 2026.

**15. The Fiscal Trap → Forced Easing Chain** — *End-to-end lag: quarters*
```
Debt/GDP ↑ → [weeks-months] → Rate Expectations ↓ (fiscal dominance priced in) → [months-quarters] → Fed Funds Rate ↓ → [days] → DXY ↓ → [hours-days] → Gold ↑↑
```
The reversal of Chain 14. When markets conclude rates MUST come down because the debt load leaves no choice.

### Tier 4: Structural/Secular Chains (slow-moving, high conviction)

**16. The Productivity → Valuation Chain** — *End-to-end lag: quarters-years*
```
Productivity Growth ↑ → [quarters] → Earnings Momentum ↑ → [days] → PE Valuations ↑ → [months] → S&P 500 ↑
                     → [quarters] → CPI ↓ (disinflationary) → [months] → Fed Funds Rate ↓
```
The AI productivity question. If it's real, it justifies everything. If not, it's a bubble.

**17. The Supply Chain → Inflation → Tightening Chain** — *End-to-end lag: months*
```
Supply Chain Pressure ↑ → [weeks-months] → CPI ↑ → [weeks-months] → Fed Funds Rate ↑ → [months] → GDP ↓
```
The 2021-22 playbook. Supply-driven inflation is harder to fight because tightening doesn't fix supply.

**18. The CRE → Bank Solvency Chain** — *End-to-end lag: months-quarters*
```
10Y Yield ↑ → [months] → CRE Stress ↑ → [weeks-months] → Regional Banks ↓ → [days-weeks] → Lending Standards ↑ → [months] → GDP ↓
```
The slow-motion crisis. Office vacancy >20%, $1.5T in maturing CRE loans, regional banks exposed.

**19. The Trade War Chain** — *End-to-end lag: weeks-months*
```
Trade Policy ↑ → [weeks] → Supply Chain Pressure ↑ → [months] → CPI ↑ + Manufacturing PMI ↓ → Stagflation dilemma
              → [hours-days] → China Equities ↓ → [days] → EM FX ↓ → [weeks] → Global Trade Volume ↓
```
Tariffs are simultaneously inflationary and growth-destructive — creating the worst policy dilemma.

**20. The Safe-Haven Rotation Chain** — *End-to-end lag: hours*
```
Shock → [hours] → VIX ↑ → [hours] → Gold ↑ + 10Y Yield ↓ + DXY ↑ (flight to safety trifecta)
```
The immediate response to any geopolitical or systemic shock.

**21. The Leverage Cascade Chain** — *End-to-end lag: hours-days*
```
S&P ↓ → [hours] → Margin Debt ↓ → [hours-days] → Forced selling → S&P ↓↓ → [hours] → HY Spread ↑ → [days] → Lending Standards ↑
```
Why leveraged corrections become liquidity crises.

**22. The QE/QT Liquidity Chain** — *End-to-end lag: days-weeks*
```
Fed Balance Sheet ↑/↓ → [days] → Bank Reserves ↑/↓ → [days] → Financial Conditions ↓/↑ → [weeks] → S&P 500 ↑/↓ + HY Spread ↓/↑
```
The liquidity tide. When all four major CBs expand, risk assets have a tailwind regardless of fundamentals.

**23. The Earnings → Equity Chain** — *End-to-end lag: weeks-months*
```
Revenue Growth → [weeks] → Earnings Momentum → [hours-days] → S&P 500 → [hours] → PE Valuations → [days] → Fund Flows
```
The fundamental equity chain. Drives the bull market between crises.

**24. The Crypto Contagion Chain** — *End-to-end lag: days-weeks*
```
Bitcoin ↓ → [hours] → Margin Debt ↓ → [days] → Private Credit ↓ (crypto lenders) → [days-weeks] → Regional Banks ↓ → [weeks] → Lending Standards ↑
```
Proven in 2022-23. Crypto is no longer isolated — it connects to traditional finance through banks and lending.

**25. The Peripheral Sovereign Chain** — *End-to-end lag: days-weeks*
```
EU Periphery Spreads ↑ → [hours-days] → EUR/USD ↓ → [hours] → FX Vol ↑ → [hours-days] → VIX ↑ → [days] → ECB forced to intervene
```
2011-12 crisis, 2022 TPI invention. The existential risk for the Euro.

---

## Causal Edge Matrix

This section documents every directed causal edge in the factor graph — approximately 1,080+ edges across 111 source factors. Each edge represents a structural transmission mechanism: a change in the source factor causally influences the target factor through the described channel.

**Reading the tables:**
- **Direction:** `+` = positive/same-direction (source ↑ → target ↑), `−` = negative/inverse (source ↑ → target ↓), `±` = complex/regime-dependent
- **Mechanism:** Brief description of the transmission channel
- Factors marked **(NEW)** are proposed additions not yet in the 52-node graph

---

### Category 1: US Macroeconomic Fundamentals

**Federal Funds Rate** (25 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Mortgage Rate | + | weeks | Pass-through via Treasury curve and MBS spread |
| Repo/SOFR Rate | + | hours | Direct floor for overnight secured funding |
| 2Y Treasury Yield | + | days | Front-end yields track expected policy path |
| 10Y Treasury Yield | + | days-weeks | Long rates rise on tighter policy, dampened by term premium |
| 30Y Treasury Yield | + | weeks | Ultra-long rates respond with lag, anchored by growth expectations |
| Real Yield | + | days | Nominal rate rises faster than breakevens adjust |
| Yield Curve Spread | − | days | Rate hikes flatten/invert curve (front end rises faster) |
| Housing Starts | − | months | Higher rates raise mortgage costs, reduce housing demand |
| Home Prices | − | quarters | Reduced affordability suppresses buyer demand |
| Consumer Confidence | − | weeks | Higher borrowing costs weigh on consumer outlook |
| S&P 500 | − | days | Higher discount rate compresses equity valuations |
| NASDAQ | − | days | Growth/tech stocks most sensitive to discount rate changes |
| Russell 2000 | − | days | Small caps rely on floating-rate debt, higher costs squeeze margins |
| IG Credit Spread | + | days-weeks | Tighter policy increases default risk perception |
| HY Credit Spread | + | days-weeks | Leveraged issuers face higher refinancing costs |
| DXY (Dollar Index) | + | days | Rate differential attracts foreign capital, strengthens dollar |
| EUR/USD | − | days | USD strength from rate differential weakens EUR |
| USD/JPY | + | days | Wider US-Japan rate gap strengthens USD vs JPY |
| EM FX Basket | − | days-weeks | Dollar strength pressures EM currencies |
| EM Sovereign Spread | + | weeks | Higher US rates increase EM debt service costs |
| Gold | − | days | Higher real rates raise opportunity cost of holding gold |
| Bitcoin | − | days | Risk-free rate competition reduces speculative appetite |
| Financial Conditions | + | weeks | Rate hikes tighten overall financial conditions |
| Rate Expectations | + | days | Current rate anchors forward expectations |
| Unemployment Rate | ± | quarters | Rate hikes slow economy → unemployment rises; rate cuts stimulate → unemployment falls. Operates with 12-18 month lag |

**US CPI Year-over-Year** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Breakeven Inflation | + | days | Market inflation expectations track realized CPI |
| Real Yield | − | days | Higher CPI erodes real return at fixed nominal yield |
| Fed Funds Rate | + | weeks-months | Above-target CPI triggers Fed tightening |
| Rate Expectations | + | hours-days | Hot CPI prints shift expected rate path higher |
| Consumer Confidence | − | days | Rising prices erode purchasing power and sentiment |
| Wage Growth | + | months | Workers demand higher wages to offset cost of living |
| Gold | + | days | Inflation hedge demand rises with CPI |
| 10Y Treasury Yield | + | days | Higher inflation expectations push nominal yields up |
| PCE Deflator | + | months | CPI and PCE are co-integrated, CPI leads expectations |

**US GDP Growth** (14 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Manufacturing PMI | + | weeks | GDP growth drives industrial activity and new orders |
| Services PMI | + | weeks | Broad growth lifts services sector output |
| Unemployment Rate | − | months | Okun's law: GDP growth reduces unemployment |
| Fiscal Deficit | − | quarters | Growth boosts tax revenue, narrowing deficit |
| Housing Starts | + | months | Economic expansion supports housing demand |
| Consumer Confidence | + | days-weeks | Growth lifts income expectations and sentiment |
| S&P 500 | + | days | Earnings growth follows economic expansion |
| Financials | + | days-weeks | Loan growth and asset quality improve with GDP |
| Revenue Growth | + | quarters | Corporate top-line tracks nominal GDP |
| Earnings Momentum | + | quarters | Revenue growth flows through to earnings |
| HY Credit Spread | − | days-weeks | Growth reduces default risk for leveraged issuers |
| EM Equities | + | days | US growth supports global demand and risk appetite |
| Fed Funds Rate | + | quarters | Strong growth gives Fed room to tighten |
| EM Sovereign Spread | − | days-weeks | US GDP weakness → global risk-off → EM spreads widen as capital flees to safety |

**Unemployment Rate** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Consumer Confidence | − | days | Rising unemployment destroys consumer sentiment |
| Rate Expectations | − | days | Higher unemployment signals dovish Fed pivot |
| HY Credit Spread | + | weeks | Rising unemployment increases default risk |
| Housing Starts | − | months | Job losses reduce housing demand |
| Wage Growth | − | months | Slack labor market reduces wage bargaining power |
| GDP Growth | − | months | Rising unemployment reduces aggregate demand |
| Retail Sentiment | − | days | Job insecurity reduces risk appetite |
| Fed Funds Rate | − | months | Fed eases to support employment mandate |
| Fiscal Deficit | + | months | Automatic stabilizers (unemployment benefits) widen deficit |
| S&P 500 | − | days | Rising unemployment signals earnings risk and recession — every major unemployment spike coincides with equity selloff |

**Manufacturing PMI** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Earnings Momentum | + | weeks | Manufacturing expansion drives industrial earnings |
| Revenue Growth | + | months | New orders translate to corporate revenue |
| Supply Chain Pressure | − | weeks | High PMI signals smooth supply chains (inverse stress) |
| Baltic Dry Index | + | weeks | Manufacturing expansion increases shipping demand |
| Iron Ore | + | days-weeks | Industrial production drives raw material demand |
| Copper | + | days-weeks | Manufacturing activity is copper-intensive |
| GDP Growth | + | months | PMI is a leading indicator of GDP |
| S&P 500 | + | days | Expansion signal supports risk assets |

**PCE Deflator** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | days | Fed's preferred inflation gauge pushes yields |
| 2Y Treasury Yield | + | days | PCE drives near-term Fed rate expectations |
| Breakeven Inflation | + | days | PCE validates or challenges market inflation expectations |
| Gold | + | days | Inflation hedge demand tracks PCE |
| Rate Expectations | + | days | Hot PCE shifts expected Fed path higher |
| Fed Funds Rate | + | weeks-months | PCE above 2% triggers/sustains tightening |

**Consumer Confidence** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | + | months | Confidence drives 70% of GDP (consumer spending) |
| Revenue Growth | + | months | Consumer spending flows to corporate top-line |
| Housing Starts | + | months | Confident consumers commit to large purchases |
| Services PMI | + | weeks | Consumer spending is primarily on services |
| Fund Flows | + | weeks | Confident consumers increase investment allocations |

**Wage Growth** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Earnings Momentum | − | quarters | Higher wages compress profit margins |
| Services PMI | + | weeks | Wage growth supports service sector demand |
| Housing Starts | + | months | Higher incomes improve housing affordability |
| Rate Expectations | + | days | Wage-price spiral risk shifts Fed expectations hawkish |
| CPI | + | months | Labor costs pass through to consumer prices |
| Consumer Confidence | + | weeks | Rising wages boost consumer outlook |
| Home Prices | + | months | Wages determine mortgage qualification amounts — higher wages increase housing demand and affordability |
| Fed Funds Rate | + | months | Wage growth is a core input to the Fed's inflation assessment — persistent wage pressure forces hawkish policy |

**Jobless Claims (NEW)** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Unemployment Rate | + | weeks | Claims are a high-frequency leading indicator of unemployment |
| Consumer Confidence | − | days | Rising claims signal labor market deterioration |
| Rate Expectations | − | days | Spiking claims signal dovish Fed shift |
| GDP Growth | − | weeks | Claims proxy for real-time economic weakness |
| Retail Sentiment | − | days | Layoff fears reduce risk appetite |
| S&P 500 | − | hours-days | Claims spikes trigger risk-off (Sahm Rule sensitivity) |
| HY Credit Spread | + | days | Rising claims increase expected default rates |

**Services PMI (NEW)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | + | months | Services are ~80% of US GDP |
| S&P 500 | + | days | Services expansion supports broad earnings |
| Earnings Momentum | + | weeks | Service sector profitability drives aggregate earnings |
| Unemployment Rate | − | months | Service sector is the largest employer |
| CPI | + | months | Services inflation is the stickiest CPI component |
| Revenue Growth | + | months | Services demand drives corporate top-line |
| Consumer Confidence | + | weeks | Service sector health reflects consumer spending |
| Rate Expectations | + | days | Strong services = persistent inflation pressure |

**Productivity (NEW)** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Wage Growth | − | quarters | Productivity gains allow higher wages without inflation |
| CPI | − | quarters | Productivity growth is disinflationary |
| Earnings Momentum | + | quarters | Output per worker gains boost profit margins |
| GDP Growth | + | quarters | Productivity is a fundamental GDP growth driver |
| Tech Sector | + | months | Tech investment is the primary productivity channel |
| Revenue Growth | + | quarters | More output per worker → more revenue per employee |
| PE Valuations | + | quarters | Higher productivity justifies higher multiples — the central AI valuation debate of 2024-25 |
| Fed Funds Rate | − | quarters | Productivity-driven growth is non-inflationary, less hawkish |

**JOLTS Job Openings (NEW)** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Wage Growth | + | months | High openings/unemployed ratio gives workers bargaining power |
| Unemployment Rate | − | months | Abundant openings reduce unemployment duration |
| Consumer Confidence | + | weeks | Plentiful jobs boost household sentiment |
| Rate Expectations | + | days | Tight labor market signals persistent inflation |
| Quits Rate → GDP | + | months | High quits signal worker confidence, economic dynamism |

**Labor Force Participation (NEW)** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Unemployment Rate | − | months | Higher participation expands labor supply, can mask weakness |
| Wage Growth | − | months | Larger labor pool reduces wage pressure |
| GDP Growth | + | quarters | More workers → higher potential output |
| CPI | − | quarters | Labor supply expansion is disinflationary |
| Fed Funds Rate | ± | quarters | Complex: higher participation reduces inflation pressure but signals growth |
| Consumer Confidence | + | months | Rising participation signals economic engagement |

---

### Category 2: Monetary Policy & Central Banks

**Fed Balance Sheet** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Bank Reserves | + | days | Asset purchases create reserves in banking system |
| Repo/SOFR Rate | − | days | Excess reserves push down overnight funding rates |
| Financial Conditions | − | weeks | Balance sheet expansion eases financial conditions |
| IG Credit Spread | − | weeks | QE portfolio rebalancing compresses credit spreads |
| HY Credit Spread | − | weeks | Reach-for-yield effect in credit markets |
| Mortgage Rate | − | weeks | MBS purchases directly compress mortgage spreads |
| Term Premium | − | weeks-months | Duration removal suppresses term premium |
| 10Y Treasury Yield | − | days-weeks | Direct price pressure from Treasury purchases |
| S&P 500 | + | days | Liquidity injection supports risk assets |
| Gold | + | days-weeks | Balance sheet expansion raises inflation expectations |
| DXY | − | days-weeks | Dollar weakens on monetary expansion |
| Bitcoin | + | days | Liquidity expansion fuels speculative assets |

**Rate Expectations (Fed Funds Futures)** (14 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 2Y Treasury Yield | + | hours-days | Front-end yields directly reflect rate expectations |
| 10Y Treasury Yield | + | days | Rate path expectations anchor long yields |
| Mortgage Rate | + | days-weeks | Mortgage rates track expected rate path + spread |
| EUR/USD | − | hours-days | Hawkish Fed expectations strengthen USD, weaken EUR |
| USD/JPY | + | hours-days | Higher expected US rates widen US-Japan differential |
| DXY | + | hours-days | Hawkish expectations attract capital to USD |
| S&P 500 | − | hours-days | Higher expected rates compress equity valuations |
| NASDAQ | − | hours-days | Growth stocks most sensitive to rate path |
| Financial Conditions | + | days | Hawkish expectations tighten financial conditions |
| REITs | − | days | Higher expected rates reduce present value of rental streams |
| Gold | − | hours-days | Higher expected real rates raise gold's opportunity cost |
| EM Sovereign Spread | + | days | Expected US rate rises pressure EM debt sustainability |
| EM FX Basket | − | days | Hawkish Fed expectations cause EM capital outflows |
| Russell 2000 | − | hours-days | Small caps sensitive to floating-rate debt costs |

**QE Pace** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Bank Reserves | + | days | Faster QE creates more reserves |
| Repo/SOFR Rate | − | days | Reserve abundance pushes funding rates to floor |
| 10Y Treasury Yield | − | days-weeks | Treasury purchases suppress yields |
| 30Y Treasury Yield | − | days-weeks | Duration removal across the curve |
| IG Credit Spread | − | weeks | Portfolio rebalancing compresses spreads |
| HY Credit Spread | − | weeks | Reach-for-yield intensifies with faster QE |
| Term Premium | − | weeks | Removing duration supply suppresses term premium |
| S&P 500 | + | days | Liquidity injection supports asset prices |
| Financial Conditions | − | weeks | QE eases financial conditions broadly |
| Gold | + | days-weeks | Inflation expectations rise with monetary expansion |
| Mortgage Rate | − | weeks | MBS purchases directly lower mortgage rates |
| DXY | − | days-weeks | Monetary expansion weakens the dollar |

**Global Central Bank Liquidity** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Equities | + | weeks | Global liquidity expansion supports EM risk assets |
| EM FX Basket | + | weeks | Liquidity flush weakens USD, supports EM currencies |
| HY Credit Spread | − | weeks | Global liquidity compresses credit risk premia |
| Bitcoin | + | days-weeks | Excess liquidity flows into speculative assets |
| Copper | + | weeks | Liquidity supports commodity speculation and demand |
| Gold | + | weeks | Central bank expansion raises debasement fears |
| S&P 500 | + | weeks | Global liquidity is a macro tailwind for equities |
| VIX | − | days-weeks | Liquidity abundance suppresses volatility |
| IG Credit Spread | − | weeks | Global reach-for-yield compresses IG spreads |
| Financial Conditions | − | weeks | Coordinated expansion eases global conditions |
| EM Sovereign Spread | − | weeks | Liquidity reduces EM refinancing risk |
| DXY | − | weeks | Non-Fed expansion narrows rate differentials |

**ECB Policy Rate (NEW)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EUR/USD | + | hours-days | Higher ECB rates strengthen euro vs dollar |
| EU HICP | − | months | Tighter policy suppresses eurozone inflation |
| Europe Equities | − | days | Higher rates compress European equity valuations |
| EU Periphery Spreads | + | days | Tighter ECB policy widens peripheral risk premia |
| IG Credit Spread | + | days-weeks | European credit spreads widen on tightening |
| Financial Conditions | + | days-weeks | ECB tightening tightens European financial conditions |
| Global CB Liquidity | ± | days | ECB QT reduces global liquidity pool |
| DXY | − | hours-days | Stronger EUR weakens DXY |

**PBOC Policy (NEW)** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| USD/CNY | − | days | PBOC easing weakens CNY vs USD |
| China PMI | + | months | Monetary stimulus supports Chinese industrial activity |
| China Credit Impulse | + | weeks-months | PBOC easing expands credit flow |
| China Property | + | months | Lower rates support property sector financing |
| Copper | + | weeks | China stimulus boosts industrial commodity demand |
| Iron Ore | + | weeks | Chinese construction and manufacturing demand rises |
| EM Equities | + | weeks | China stimulus spills over to EM demand |
| Global CB Liquidity | + | days | PBOC expansion adds to global liquidity pool |
| EM FX Basket | + | weeks | Chinese demand supports EM export economies |
| Global Trade Volume | + | months | Chinese demand is a major global trade driver |

**Term Premium (NEW)** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | days | Term premium is a direct component of long yields |
| 30Y Treasury Yield | + | days | Ultra-long bonds most sensitive to term premium |
| Yield Curve Spread | + | days | Rising term premium steepens the curve |
| Mortgage Rate | + | days-weeks | Mortgage rates include term premium component |
| S&P 500 | − | days | Higher term premium raises equity discount rate |
| REITs | − | days | Rate-sensitive REITs suffer from term premium rises |
| MOVE Index | + | days | Term premium volatility drives rate vol |
| Financial Conditions | + | days-weeks | Rising term premium tightens financial conditions |
| IG Credit Spread | + | days-weeks | Credit spreads widen as risk-free rate rises |
| DXY | + | days | Higher term premium attracts foreign capital |
| Gold | − | days | Higher real long-term rates raise gold's opportunity cost |

---

### Category 3: Rates, Credit & Housing

**2-Year Treasury Yield** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Yield Curve Spread | − | hours | Rising 2Y (front end) flattens/inverts curve |
| Mortgage Rate | + | days | Short-rate expectations anchor mortgage pricing |
| Repo/SOFR Rate | + | hours | Front-end yields and repo rates are tightly linked |
| DXY | + | hours-days | Higher short rates attract carry trade capital |
| Financials | + | days | Banks earn more on short-duration assets |
| Gold | − | hours-days | Higher short-term real rates raise gold's opportunity cost |
| EM Sovereign Spread | + | days | Rising US short rates tighten EM financing |
| S&P 500 | − | hours-days | Higher risk-free rate compresses equity valuations |
| NASDAQ | − | hours-days | Growth stocks sensitive to front-end rate moves |
| IG Credit Spread | + | days | Rising rates increase corporate refinancing risk |
| Consumer Confidence | − | weeks | Higher borrowing costs weigh on sentiment |
| EUR/USD | − | hours-days | USD strength from rate differential |

**10-Year Treasury Yield** (20 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Mortgage Rate | + | days-weeks | 30Y mortgage rate tracks 10Y yield + MBS spread |
| S&P 500 | − | hours-days | Equity risk premium compresses as discount rate rises |
| NASDAQ | − | hours-days | Long-duration growth stocks most rate-sensitive |
| PE Valuations | − | days | Higher discount rate compresses PE multiples |
| Equity Risk Premium | − | days | ERP = earnings yield minus 10Y yield |
| Gold | − | hours-days | Nominal yield rise increases gold's opportunity cost |
| Housing Starts | − | months | Higher rates crush housing affordability |
| CRE Stress | + | months | Higher cap rates stress commercial property values |
| REITs | − | days | REITs priced as yield instruments, compete with Treasuries |
| DXY | + | hours-days | Higher US yields attract global capital |
| EM Sovereign Spread | + | days | EM debt repriced relative to US risk-free rate |
| EM FX Basket | − | days | Yield differential drives capital out of EM |
| Fiscal Deficit | + | quarters | Higher debt service costs widen deficit |
| Financials | ± | days | NIMs improve but bond portfolio losses (SVB dynamic) |
| Home Prices | − | months | Affordability erosion suppresses home prices |
| 30Y Treasury Yield | + | hours | Long-end yields are correlated across maturity |
| Breakeven Inflation | ± | days | Nominal yield = real yield + breakeven |
| IG Credit Spread | + | days | Rising rates increase corporate debt burden |
| Europe Equities | − | days | Global rate spillover affects European valuations |
| Japan Equities | − | days | US-Japan rate differential affects carry trades |

**30-Year Treasury Yield** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Mortgage Rate | + | days | Ultra-long rate anchors 30Y fixed mortgage pricing |
| REITs | − | days | REITs compete with ultra-long bond yields |
| CRE Stress | + | months | Higher long rates stress CRE cap rates |
| PE Valuations | − | days | Long-term discount rate compresses multiples |
| Home Prices | − | months | Mortgage affordability erodes with ultra-long rates |
| Fiscal Deficit | + | quarters | Higher long-term debt service costs |
| Term Premium | + | days | 30Y yield is most term-premium-sensitive maturity |

**Yield Curve Spread (10Y-2Y)** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Financials | + | days-weeks | Steeper curve improves bank NIMs |
| Regional Banks | + | days-weeks | Regional banks most dependent on curve steepness for NIMs |
| Lending Standards | − | weeks-months | Steeper curve incentivizes lending (higher NIM reward) |
| Russell 2000 | + | days | Small caps benefit from bank lending expansion |
| GDP Growth | + | months | Steeper curve signals economic expansion expectations |
| Recession Probability | − | months | Inversion is the most reliable recession predictor |
| S&P 500 | + | days | Curve steepening signals growth, supports equities |
| Consumer Confidence | + | weeks | Normal curve signals healthy economy |
| HY Credit Spread | − | days-weeks | Curve steepening reduces recession/default expectations |

**IG Credit Spread** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| HY Credit Spread | + | hours-days | IG widening signals broader credit stress |
| S&P 500 | − | hours-days | Wider credit spreads signal risk aversion |
| Financials | − | days | Bank credit portfolios lose value |
| Buybacks | − | weeks | Higher borrowing costs reduce buyback financing |
| Financial Conditions | + | days | Wider spreads tighten financial conditions |
| CDS Spreads | + | hours-days | Credit stress reprices default insurance |
| CP Spread | + | days | Commercial paper spreads widen sympathetically |
| Private Credit | + | days-weeks | Stress reprices private lending risk |
| Earnings Momentum | − | weeks | Higher corporate funding costs compress margins |
| Revenue Growth | − | months | Credit tightening reduces economic activity |
| Fund Flows | − | days | IG spread widening triggers bond fund redemptions and capital flight from credit |

**HY Credit Spread** (14 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | − | hours-days | HY spread is a leading risk appetite indicator |
| Russell 2000 | − | hours-days | Small caps are quasi-HY credit instruments |
| VIX | + | hours | Credit stress amplifies equity volatility |
| CDS Spreads | + | hours | HY stress reprices default swap markets |
| Financial Conditions | + | days | Wider HY spreads tighten conditions |
| Lending Standards | + | weeks | Banks tighten lending when HY signals stress |
| Earnings Momentum | − | weeks | Higher funding costs compress earnings |
| IPO Issuance | − | weeks | Credit stress freezes IPO market |
| Private Credit | + | days-weeks | HY stress reprices private credit risk |
| EM Sovereign Spread | + | days | HY stress signals global risk aversion |
| Regional Banks | − | days | Leveraged loan portfolios deteriorate |
| Energy Sector | − | days | Energy is the largest HY sector |
| IG Credit Spread | + | hours-days | HY widening signals broader credit stress that cascades to investment grade (every credit crisis since 1998) |
| GDP Growth | − | months | Financial accelerator — wider HY → tighter conditions → weaker growth → wider HY (self-reinforcing in crises) |

**Real Yield (TIPS)** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Gold | − | hours-days | Gold is a zero-coupon real asset — competes with real yield |
| S&P 500 | − | hours-days | Higher real rates raise true discount rate for equities |
| NASDAQ | − | hours-days | Long-duration tech stocks most sensitive to real rates |
| DXY | + | hours-days | Higher real yields attract foreign capital |
| PE Valuations | − | days | Real discount rate compresses multiples |
| Bitcoin | − | hours-days | Positive real yields reduce appeal of non-yielding assets |
| EM Sovereign Spread | + | days | Higher US real rates tighten EM financial conditions |
| EM FX Basket | − | days | Real rate differential drives EM capital outflows |
| REITs | − | days | Higher real rates compress REIT valuations |
| Equity Risk Premium | − | days | ERP shrinks as real rates rise |
| Copper | − | days-weeks | Higher real rates suppress commodity speculation |
| Tech Sector | − | hours-days | Growth stocks' future cash flows discounted more heavily |

**Breakeven Inflation** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | hours | Rising breakevens push nominal yields higher |
| Gold | + | hours-days | Inflation expectations drive gold demand |
| Brent Crude Oil | + | days | Oil and breakevens are co-integrated |
| Rate Expectations | + | hours-days | Rising inflation expectations shift Fed path hawkish |
| DXY | − | days | Higher inflation expectations weaken purchasing power |
| CPI | + | months | Breakevens reflect and reinforce inflation expectations |
| Consumer Confidence | − | days | Expected inflation erodes purchasing power outlook |
| Energy Sector | + | days | Energy assets are inflation beneficiaries |
| Bitcoin | + | days | Inflation expectations drive crypto inflation-hedge narrative |
| Fed Funds Rate | + | months | Persistent breakeven rises trigger Fed tightening |

**5Y5Y Forward Inflation** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Fed Funds Rate | + | months | If 5Y5Y unanchors above 2.5%, Fed forced to respond regardless of employment |
| Rate Expectations | + | days | Long-run inflation expectations shift the entire rate path |
| 10Y Treasury Yield | + | days | Long-run inflation component embedded in nominal yields |
| Gold | + | days | Long-run inflation expectations drive structural gold demand |
| Consumer Confidence | − | weeks | Unanchored long-run expectations signal lost credibility |

**EM Sovereign Spread** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Equities | − | hours-days | Wider spreads signal EM risk, suppress equity valuations |
| EM FX Basket | − | hours-days | Spread widening triggers EM capital flight |
| Fund Flows | − | days | Wider EM spreads cause portfolio rebalancing away from EM |
| China Equities | − | days | China-specific risk repriced in EM stress |
| Copper | − | days-weeks | EM stress reduces commodity demand expectations |
| VIX | + | days | EM contagion risk raises global volatility |
| HY Credit Spread | + | days | EM stress is a global credit risk transmission channel |
| Financials | − | days-weeks | US/EU banks have material EM loan exposure — 1982 LatAm crisis nearly wiped out Citibank; 1997 Asian crisis hit Japanese banks; EM sovereign default cascades to developed-market bank balance sheets |

**Housing Starts** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | + | months | Residential construction is a GDP component |
| Home Prices | + | months | More supply initially signals demand; shortage → price up |
| Copper | + | weeks | Residential construction is copper-intensive |
| Unemployment Rate | − | months | Construction employs millions directly |
| Iron Ore | + | weeks | Steel demand for construction |
| Consumer Confidence | + | weeks | Housing activity signals economic health |
| Lumber/Timber | + | days-weeks | Direct input demand (proxy: lumber futures, not a standalone factor) |

**Home Prices (Case-Shiller)** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Consumer Confidence | + | weeks | Wealth effect from homeownership |
| CPI | + | months | Shelter inflation = 40% of CPI |
| PCE Deflator | + | months | Shelter component in PCE |
| GDP Growth | + | months | Wealth effect supports consumer spending |
| REITs | + | days-weeks | Residential REITs track home price trends |
| Housing Starts | + | months | Rising prices incentivize new construction |
| Financials | + | weeks | Mortgage portfolio values increase |
| Regional Banks | + | weeks | Mortgage collateral values improve |
| Retail Sentiment | + | weeks | Household wealth drives risk appetite |
| Lending Standards | ± | months | Home prices affect collateral values (LTV ratios) which determine bank willingness to lend — rising prices loosen, falling prices tighten |

**Mortgage Rate (30Y Fixed)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Housing Starts | − | weeks-months | Higher mortgage rates kill housing demand |
| Home Prices | − | months | Affordability erosion suppresses prices |
| Consumer Confidence | − | weeks | Monthly payment burden affects sentiment |
| GDP Growth | − | months | Housing sector contraction drags GDP |
| REITs | − | days-weeks | Residential REITs suffer from housing slowdown |
| Financials | ± | weeks | Higher rates boost NIM but reduce origination volume |
| Regional Banks | ± | weeks | Same NIM vs. volume tradeoff |
| CRE Stress | + | weeks-months | Rate pass-through to commercial mortgages |

**Commercial Real Estate Stress** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Regional Banks | − | weeks-months | CRE is ~30% of regional bank loan portfolios |
| Financials | − | weeks | Large bank CRE exposure via CMBS |
| Lending Standards | + | weeks | CRE losses trigger bank deleveraging |
| IG Credit Spread | + | days-weeks | CRE stress reprices corporate credit risk |
| HY Credit Spread | + | days-weeks | CRE-linked HY bonds sell off |
| REITs | − | days | Direct mark-to-market on property values |
| Financial Conditions | + | weeks | CRE stress tightens conditions via bank channel |
| GDP Growth | − | months | Construction contraction and reduced business investment |
| Private Credit | + | weeks | Private CRE lenders face writedowns |
| CDS Spreads | + | days-weeks | Bank CDS widens on CRE exposure |

**Financial Conditions Index (FCI)** (17 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | − | weeks-months | Tighter FCI constrains economic activity |
| S&P 500 | − | hours-days | Tighter conditions suppress equity prices |
| Russell 2000 | − | hours-days | Small caps most sensitive to financial conditions |
| HY Credit Spread | + | days | Tight FCI pushes out credit spreads |
| Housing Starts | − | months | Tighter conditions reduce mortgage availability |
| Consumer Confidence | − | weeks | Credit tightening weighs on sentiment |
| Earnings Momentum | − | weeks | Tighter conditions compress corporate earnings |
| IPO Issuance | − | weeks | Tight conditions freeze new issuance |
| Buybacks | − | weeks | Higher borrowing costs reduce buyback funding |
| Lending Standards | + | weeks | Banks respond to tight FCI by tightening further (co-reinforcing) |
| Private Credit | + | days-weeks | FCI tightening reprices private lending |
| Financials | − | days | Tight financial conditions hit bank earnings, credit quality, and capital markets revenue |

**Bank Lending Standards** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | − | months | Tighter lending suppresses investment and consumption |
| Housing Starts | − | months | Tighter construction and mortgage lending |
| CRE Stress | + | months | Tighter lending = CRE refinancing risk |
| Russell 2000 | − | weeks | Small caps rely on bank lending |
| IG Credit Spread | + | weeks | Tighter lending pushes borrowers to bond market |
| HY Credit Spread | + | weeks | Credit rationing reprices high-yield risk |
| Unemployment Rate | + | months | Credit contraction leads to layoffs |
| Consumer Confidence | − | weeks | Credit availability affects sentiment |
| Revenue Growth | − | months | Less credit = less economic activity |
| Private Credit | + | weeks | Shadow lending grows when banks retreat |
| Financial Conditions | + | weeks | Bank lending tightening IS financial conditions tightening — lending standards are a core FCI component |

**Bank Reserves** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Repo/SOFR Rate | − | hours | Abundant reserves suppress overnight funding rates |
| TED Spread | − | hours-days | Ample reserves reduce interbank stress |
| Financial Conditions | − | days | Reserve abundance eases conditions |
| Lending Standards | − | weeks | Banks with ample reserves lend more freely |
| S&P 500 | + | days | Reserve abundance is a liquidity tailwind |
| VIX | − | days | Plentiful reserves suppress systemic risk fears |
| CP Spread | − | hours-days | Ample reserves ease commercial paper markets |

**Repo/SOFR Rate** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 2Y Treasury Yield | + | hours | Repo rate anchors very short-term yield expectations |
| TED Spread | + | hours | Repo stress widens interbank risk premia |
| CP Spread | + | hours | Repo stress transmits to commercial paper market |
| Financial Conditions | + | hours-days | Repo rate spikes tighten conditions (Sept 2019 example) |
| Fund Flows | − | days | Higher funding costs reduce leveraged fund activity |
| Bank Reserves | − | days | High repo rates signal reserve scarcity |
| Private Credit | + | days-weeks | Funding cost pass-through to leveraged lending |
| IG Credit Spread | + | hours-days | Repo stress widens investment-grade spreads |

**TED Spread** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Financial Conditions | + | hours-days | TED spread is a core FCI component |
| IG Credit Spread | + | hours-days | Interbank stress transmits to corporate credit |
| HY Credit Spread | + | hours-days | Bank stress amplifies credit risk repricing |
| Lending Standards | + | days-weeks | Banks tighten lending during interbank stress |
| VIX | + | hours-days | Banking stress raises equity volatility |
| S&P 500 | − | hours-days | Bank stress is a systemic risk signal |
| Financials | − | hours-days | Direct indicator of bank sector stress |
| CP Spread | + | hours | Short-term funding stress is interconnected |
| Regional Banks | − | hours-days | Smaller banks more vulnerable to funding stress |

**Commercial Paper Spread** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Financial Conditions | + | hours-days | CP stress tightens short-term funding conditions |
| IG Credit Spread | + | hours-days | CP stress signals broader corporate funding pressure |
| Earnings Momentum | − | weeks | Higher funding costs compress margins |
| Revenue Growth | − | months | Working capital stress constrains business activity |
| S&P 500 | − | hours-days | Corporate funding stress weighs on equities |
| Fund Flows | − | days | Higher CP rates reduce leveraged positioning |
| Lending Standards | + | days-weeks | CP stress causes banks to ration credit |

**Private Credit** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| HY Credit Spread | + | days-weeks | Private credit stress reprices public HY risk |
| Lending Standards | + | weeks | Private credit losses trigger bank re-evaluation |
| Russell 2000 | − | days-weeks | Small caps rely on private credit for financing |
| Financial Conditions | + | weeks | Private credit stress tightens conditions |
| Earnings Momentum | − | months | Borrower stress reduces earnings quality |
| CDS Spreads | + | days-weeks | Private credit losses increase default expectations |
| Regional Banks | − | weeks | Banks with private credit fund exposure lose |
| IPO Issuance | − | weeks | Private credit stress freezes exit markets |

**Money Market Fund Flows** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Bank Reserves | − | days | Deposit flight from banks to MMFs drains bank reserves (SVB: $500B in one week) |
| Lending Standards | + | weeks | Deposit outflows force banks to tighten lending |
| Regional Banks | − | days-weeks | MMF competition for deposits is existential for smaller banks |
| Financials | − | days-weeks | Bank disintermediation reduces fee income and lending capacity |
| Repo/SOFR Rate | − | days | MMF inflows into overnight repo push SOFR down (MMFs are primary repo lenders) |
| Financial Conditions | ± | days-weeks | Outflows from MMFs back into equities ease conditions; inflows to MMFs tighten bank funding |
| S&P 500 | ± | days | MMF outflows back to equities fuel rallies; MMF inflows signal risk-off |

---

### Category 4: Geopolitics, Fiscal Policy & Supply Chain

**Geopolitical Risk Index** (21 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Brent Crude Oil | + | hours | Every Middle East/energy-region conflict since 1973 has spiked oil — supply disruption and risk premium |
| Gold | + | hours | Canonical safe-haven trade — war drives physical and ETF gold buying |
| DXY | + | hours | Risk-off drives dollar safe-haven bid (except in US-specific political crises) |
| 10Y Treasury Yield | − | hours | Flight-to-quality bid compresses Treasury yields during geopolitical crises |
| VIX | + | hours | Geopolitical shocks spike implied equity volatility on same-day |
| S&P 500 | − | hours | Risk-off repricing on geopolitical escalation |
| Natural Gas | + | hours-days | Supply disruption fears (Middle East, Russia) |
| IG Credit Spread | + | hours-days | Uncertainty premium widens credit spreads |
| HY Credit Spread | + | hours-days | Risk aversion reprices high-yield debt |
| MOVE Index | + | hours | Geopolitical uncertainty raises rate volatility |
| SKEW | + | hours-days | Tail risk hedging demand increases |
| EM Sovereign Spread | + | hours-days | EM perceived as most vulnerable in crises |
| EM Equities | − | hours-days | Capital flight from EM during geopolitical stress |
| EM FX Basket | − | hours-days | EM currency depreciation on risk-off |
| Fund Flows | − | days | Risk-off triggers EM and equity fund outflows |
| FX Volatility | + | hours | Geopolitical uncertainty raises currency vol |
| Uranium | + | days-weeks | Nuclear/energy security premium |
| Retail Sentiment | − | hours-days | Fear drives retail investor risk aversion |
| Consumer Confidence | − | days-weeks | Geopolitical fears weigh on economic outlook |
| Financial Conditions | + | days | Geopolitical stress tightens conditions |
| Sanctions | + | days-weeks | Geopolitical escalation triggers sanctions imposition — every major conflict since 2014 has been followed by sanctions |

**Trade Policy Uncertainty** (19 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | months | Tariffs are a direct pass-through to consumer prices |
| PCE Deflator | + | months | Import price increases flow through to PCE |
| Supply Chain Pressure | + | weeks | Trade barriers disrupt supply chains |
| Copper | − | days-weeks | Trade wars reduce global industrial demand |
| Earnings Momentum | − | weeks-months | Tariff uncertainty depresses capex and margins |
| Revenue Growth | − | months | Trade barriers reduce global revenue |
| DXY | ± | days | Complex: tariffs can strengthen USD (demand) or weaken (retaliation) |
| Semiconductors | − | weeks | Export controls restrict semis supply chains |
| Tech Sector | − | days-weeks | Tech most exposed to US-China trade restrictions |
| Global Trade Volume | − | weeks-months | Trade barriers directly reduce trade volume |
| Europe Equities | − | days | Export-dependent Europe hurt by trade wars |
| China Equities | − | hours-days | China is the primary trade war target |
| EM Equities | − | days | EM export economies suffer from trade disruption |
| EM FX Basket | − | days | Trade-dependent EM currencies weaken |
| Russell 2000 | ± | days | Domestic-focused but hurt by input cost inflation |
| Baltic Dry Index | − | weeks | Reduced trade volume depresses shipping rates |
| Iron Ore | − | days-weeks | Trade disruption reduces industrial commodity demand |
| Consumer Confidence | − | days-weeks | Trade uncertainty weighs on economic outlook |
| Manufacturing PMI | − | weeks-months | Tariffs directly hit manufacturing through input cost pressure and supply chain disruption (2018-19, 2025) |

**US Political Risk** (14 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | days | Political instability → fiscal premium on bonds |
| 30Y Treasury Yield | + | days | Longer-duration bonds most sensitive to political risk |
| IG Credit Spread | + | days | Uncertainty premium widens corporate spreads |
| HY Credit Spread | + | days | Risk aversion reprices leveraged credit |
| MOVE Index | + | days | Policy uncertainty raises rate volatility |
| Consumer Confidence | − | days-weeks | Political turmoil reduces household sentiment |
| Gold | + | hours-days | Safe-haven demand rises on political risk |
| Treasury Issuance | + | weeks-months | Debt ceiling/fiscal fights affect issuance patterns |
| PE Valuations | − | days | Uncertainty compresses valuation multiples |
| Financial Conditions | + | days | Political risk tightens financial conditions |
| REITs | − | days-weeks | Policy uncertainty depresses real estate investment |
| Healthcare | ± | days | Sector exposed to regulatory/legislative changes |
| Lending Standards | + | weeks | Banks tighten in uncertain political environment |
| Sanctions | ± | weeks-months | US political decisions drive the sanctions regime — executive orders, congressional authorization, diplomatic leverage |

**Sanctions Regime** (17 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Brent Crude Oil | + | days-weeks | Iranian/Russian sanctions directly restrict oil supply — the single most important sanctions transmission |
| Natural Gas | + | weeks-months | Russia sanctions restructured the entire European gas market (Nord Stream, LNG rerouting) |
| Gold | + | days-weeks | Central bank reserve diversification away from USD post-sanctions drives structural gold buying |
| EM Sovereign Spread | + | days-weeks | Sanctions increase EM refinancing risk |
| EM FX Basket | − | days-weeks | Sanctions trigger EM capital flight |
| EM Equities | − | days-weeks | Sanctioned countries' markets sell off, contagion spreads |
| USD/CNY | + | days | Sanctions strengthen USD as reserve/safe-haven |
| Supply Chain Pressure | + | weeks-months | Sanctions disrupt raw material and component supply |
| Uranium | + | weeks-months | Russia sanctions restrict enriched uranium supply |
| Lithium | + | weeks-months | Sanctions can disrupt critical mineral supply chains |
| Copper | + | weeks | Supply disruption from sanctioned producers |
| Global Trade Volume | − | weeks-months | Sanctions directly reduce trade flow |
| Financial Conditions | + | days-weeks | Sanctions tighten conditions for affected regions |
| Bitcoin | + | days | Sanctions evasion narrative drives crypto demand |
| Europe Equities | − | days-weeks | European firms exposed to sanctioned trade partners |
| Iron Ore | ± | weeks | Supply disruption vs. demand destruction |
| CPI | + | months | Sanctions disrupt supply chains and commodity flows → cost-push inflation (Russia sanctions → energy/food prices) |

**Climate Policy** (15 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Energy Sector | ± | months | Transition costs hurt legacy energy, benefit renewables |
| Brent Crude Oil | − | months-quarters | Demand destruction from decarbonization policies |
| Natural Gas | ± | months | Transition fuel (bridge) vs. long-term demand destruction |
| Copper | + | months | Electrification requires massive copper investment |
| Lithium | + | months | EV battery demand driven by climate mandates |
| Uranium | + | months | Nuclear renaissance as climate-friendly baseload |
| CPI | + | months | Carbon taxes and green mandates raise consumer costs |
| IG Credit Spread | + | weeks-months | Stranded asset risk reprices energy credit |
| REITs | − | months | Building efficiency mandates raise capex |
| Semiconductors | + | months | Power management chips essential for green tech |
| Housing Starts | ± | months | Green building mandates raise costs but green subsidies offset |
| Earnings Momentum | ± | months | Winners (clean tech) vs. losers (fossil fuel) |
| Tech Sector | + | months | Clean tech investment benefits technology broadly |
| Fiscal Deficit | + | quarters | Green subsidies (IRA) widen fiscal deficit |
| Gold | + | months | Fiscal expansion from climate spending raises inflation fears |
| Geopolitical Risk | + | months-quarters | Climate migration, water stress, and resource competition are emerging geopolitical triggers — Sahel instability, South Asian water disputes, Arctic resource competition |

**Tech Regulation** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Tech Sector | − | days-weeks | Regulation caps growth, increases compliance costs |
| NASDAQ | − | days | Tech-heavy index directly exposed |
| Semiconductors | − | weeks-months | Export controls restrict chips supply chains |
| S&P 500 | − | days | Tech is 30%+ of S&P 500 by weight |
| PE Valuations | − | days | Regulatory overhang compresses tech multiples |
| Earnings Momentum | − | weeks-months | Compliance costs and growth caps reduce earnings |
| China Equities | − | days-weeks | US-China tech decoupling restricts market access |
| IPO Issuance | − | weeks | Regulatory uncertainty freezes tech IPO pipeline |
| Private Credit | − | weeks | Reduced tech venture lending on regulatory risk |
| Buybacks | − | weeks | Regulated firms face restrictions on capital return |
| VIX | + | days | Regulatory uncertainty raises equity volatility |

**Fiscal Deficit** (15 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Treasury Issuance | + | weeks | Wider deficit requires more borrowing |
| Debt-to-GDP Ratio | + | quarters | Persistent deficits accumulate debt |
| 10Y Treasury Yield | + | days-weeks | Supply effect: more issuance pushes yields up |
| 30Y Treasury Yield | + | days-weeks | Long-term fiscal sustainability premium |
| Term Premium | + | weeks | Fiscal risk raises term premium |
| Breakeven Inflation | + | weeks | Deficit monetization fears raise inflation expectations |
| DXY | − | weeks-months | Fiscal deterioration undermines dollar credibility |
| Gold | + | days-weeks | Fiscal sustainability concerns drive safe-haven demand |
| Real Yield | + | days-weeks | Risk premium on Treasuries rises |
| IG Credit Spread | + | weeks | Government credit risk reprices corporate spreads |
| GDP Growth | + | months | Short-term fiscal stimulus supports growth |
| CPI | + | months | Fiscal expansion can be inflationary |
| Rate Expectations | ± | weeks | Fiscal dominance — markets price in that unsustainable debt service will eventually FORCE rate cuts regardless of inflation. The "mathematical trap": if rates rise, interest burden becomes unsustainable; if rates fall, inflation reignites. The moment markets conclude rates must come down not because inflation is beaten but because the debt load leaves no choice, rate expectations collapse |
| Fed Funds Rate | ± | months-quarters | Fiscal dominance constrains the Fed — at extreme deficit levels, aggressive rate hikes become self-defeating (higher rates → higher debt service → larger deficit → more issuance → higher yields → even higher debt service). The Fed loses degrees of freedom |
| HY Credit Spread | + | weeks | Fiscal crowding out — government borrowing competes with corporate credit for capital |

**Debt-to-GDP Ratio** (13 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Term Premium | + | weeks-months | Debt sustainability concerns raise risk premium |
| 10Y Treasury Yield | + | weeks | Sovereign credit risk premium in yields |
| 30Y Treasury Yield | + | weeks | Longest-duration bonds most sensitive to fiscal risk |
| DXY | − | months | Credibility erosion weakens reserve currency status |
| Gold | + | weeks | Sovereign risk drives gold demand |
| CDS Spreads | + | weeks | Sovereign CDS widens on debt trajectory |
| Breakeven Inflation | + | weeks | Debt monetization expectations rise |
| Fiscal Deficit | + | quarters | Debt service costs create self-reinforcing deficits |
| Financial Conditions | + | weeks | Fiscal risk tightens conditions |
| Bitcoin | + | weeks | Alternative asset narrative strengthens on sovereign risk |
| Rate Expectations | ± | weeks-months | The "mathematical trap" — at 120%+ debt/GDP with $9.2T rolling over annually, markets price in that rates MUST eventually come down not because inflation is beaten but because the debt load leaves no choice. This shifts rate expectations independently of inflation data |
| Fed Funds Rate | ± | months-quarters | Fiscal dominance — extreme debt/GDP constrains Fed independence. The Fed cannot aggressively fight inflation if doing so triggers a sovereign debt spiral. This is the mechanism that eventually forces rate cuts |
| IG Credit Spread | + | weeks | Higher sovereign debt levels raise the credit risk baseline for all corporate issuers |

**Treasury Issuance** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | days | Supply pressure pushes yields up |
| 30Y Treasury Yield | + | days | Long-end supply is most impactful |
| 2Y Treasury Yield | + | days | Bill/note issuance affects front-end rates |
| Term Premium | + | days-weeks | Duration supply raises term premium |
| MOVE Index | + | days | Auction uncertainty raises rate volatility |
| Repo/SOFR Rate | + | days | Treasury supply absorbs reserves, pressures repo |
| Bank Reserves | − | days | Reserve drain from Treasury settlement |
| IG Credit Spread | + | days-weeks | Government supply crowds out corporate bonds |
| Financial Conditions | + | days | Heavy issuance tightens conditions |
| S&P 500 | − | days | Higher rates from supply compete with equities |
| Fund Flows | − | days | Treasury supply absorbs investment capital |

**Government Spending** (13 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | + | months | Direct fiscal multiplier on output |
| Fiscal Deficit | + | quarters | Spending widens the deficit |
| CPI | + | months | Demand-pull inflation from fiscal expansion |
| Unemployment Rate | − | months | Government hiring and project employment |
| Wage Growth | + | months | Government wage competition tightens labor market |
| Manufacturing PMI | + | months | Defense/infrastructure spending supports manufacturing |
| Housing Starts | + | months | Housing subsidies and infrastructure adjacency |
| Copper | + | months | Infrastructure spending is copper-intensive |
| Consumer Confidence | + | weeks | Fiscal support lifts sentiment |
| Healthcare | + | months | Healthcare spending is a major government expenditure |
| Rate Expectations | + | weeks-months | Fiscal expansion creates hawkish Fed pressure |
| Semiconductors | + | months | CHIPS Act and defense spending benefit semis |
| Treasury Issuance | + | weeks | Spending requires Treasury financing |

**Supply Chain Pressure Index** (16 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | weeks-months | Supply bottlenecks raise consumer goods prices |
| PCE Deflator | + | weeks-months | Supply-side inflation flows through to PCE |
| Manufacturing PMI | − | weeks | Supply constraints reduce manufacturing output |
| Earnings Momentum | − | weeks | Input cost inflation compresses margins |
| Revenue Growth | ± | weeks-months | Pricing power offsets volume declines |
| Copper | + | days-weeks | Supply bottleneck reprices industrial metals |
| Semiconductors | − | weeks | Chip shortages are a key supply chain risk |
| S&P 500 | − | days | Supply stress weighs on corporate earnings |
| Consumer Confidence | − | days-weeks | Product shortages and price spikes hurt sentiment |
| GDP Growth | − | months | Supply constraints are a negative supply shock |
| Brent Crude Oil | + | days-weeks | Energy supply disruptions raise oil prices |
| Natural Gas | + | days-weeks | Energy supply chain disruption |
| Baltic Dry Index | + | days-weeks | Shipping bottlenecks raise freight rates |
| China PMI | − | weeks | Supply chain stress signals China production disruption |
| Rate Expectations | + | weeks | Supply-side inflation complicates Fed easing |
| VIX | + | days | Supply chain disruptions spike equity volatility — COVID shipping crisis, Suez blockage, semiconductor shortages |

**Baltic Dry Index** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Global Trade Volume | + | weeks | Shipping rates proxy for global trade activity |
| Iron Ore | + | days | Dry bulk shipping = iron ore + coal demand |
| Copper | + | days | Industrial commodity demand indicator |
| China PMI | + | weeks | China is the largest dry bulk importer |
| Manufacturing PMI | + | weeks | Shipping activity signals industrial demand |
| Energy Sector | + | weeks | Shipping demand indicates energy consumption |
| EM Equities | + | days-weeks | Trade activity benefits EM export economies |
| Wheat | + | days-weeks | Grain shipping costs affect food prices |
| CPI | + | weeks-months | Freight costs pass through to consumer goods |
| Supply Chain Pressure | + | days-weeks | Baltic Dry inversely reflects supply chain ease |

**Container Shipping Rates (Freightos/Drewry)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | months | Container rates are a direct pass-through to goods prices with 2-3 month lag |
| PCE Deflator | + | months | Import cost pass-through to consumer spending deflator |
| Supply Chain Pressure | + | days-weeks | Container rates are a component of the NY Fed GSCPI |
| Earnings Momentum | − | weeks-months | Higher shipping costs compress margins for import-dependent companies |
| Consumer Confidence | − | weeks | Goods price increases from shipping costs are visible to consumers |
| Revenue Growth | ± | months | Pricing power may offset volume declines for some companies |
| Retail Sentiment | − | weeks | Supply delays and price increases frustrate consumers |
| Global Trade Volume | − | weeks | Prohibitively high shipping costs reduce trade volumes |

---

### Category 5: Commodities & Currencies

**Brent Crude Oil** (19 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | weeks-months | Energy is a direct CPI component |
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
| Fed Funds Rate | ± | Oil shocks directly move Fed policy — 1973/1979 forced accommodation, 2022 forced tightening. Sign depends on growth vs inflation regime |

**Gold** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| DXY | − | hours-days | Gold and dollar are inversely correlated |
| Breakeven Inflation | + | days | Gold demand signals inflation expectations |
| EM FX Basket | + | days | Gold strength signals dollar weakness → EM benefit |
| Retail Sentiment | + | hours-days | Gold rallies excite retail safe-haven interest |
| Bitcoin | + | hours-days | Alternative asset narrative co-movement |
| Institutional Positioning | ± | days | COT data shows institutional gold sentiment |
| Mining Equities | + | hours | Gold price drives mining sector profitability |

**Copper** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | + | weeks | Copper demand proxy for Chinese industrial activity |
| Manufacturing PMI | + | weeks | Dr. Copper: industrial activity barometer |
| Housing Starts | + | months | Copper demand from residential wiring |
| CPI | + | weeks-months | Copper costs flow through to manufactured goods |
| Iron Ore | + | days | Industrial commodity complex co-moves |
| Semiconductors | + | weeks | Copper is a semiconductor manufacturing input |
| EM Equities | + | days-weeks | Copper exporters (Chile, Peru) benefit |
| Lithium | + | days-weeks | EV metals complex co-movement |
| Supply Chain Pressure | + | days-weeks | Copper bottlenecks signal supply chain stress |
| Baltic Dry Index | + | days | Copper shipping demand drives dry bulk rates |

**Natural Gas** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | weeks-months | Utilities/heating costs are CPI components |
| PCE Deflator | + | weeks-months | Energy cost pass-through |
| Energy Sector | + | hours-days | Gas is a major revenue source for utilities/E&P |
| EU HICP | + | weeks-months | European inflation heavily gas-dependent |
| Manufacturing PMI | − | weeks | High gas prices raise industrial costs |
| Consumer Confidence | − | days-weeks | Heating/utility bills weigh on sentiment |
| Wheat | + | months | Fertilizer production requires natural gas |
| Soybeans | + | months | Agricultural input cost linkage |
| Housing Starts | − | months | Higher utility costs reduce housing attractiveness |
| Uranium | + | weeks-months | Gas price spikes boost nuclear competitiveness |
| Breakeven Inflation | + | days | Gas-driven inflation expectations |

**Wheat** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | weeks | Food price inflation component |
| PCE Deflator | + | weeks | Food cost pass-through |
| EM Sovereign Spread | + | weeks | Food-importing EM nations face balance of payments stress |
| Consumer Confidence | − | days | Food price spikes are highly visible inflation |
| Geopolitical Risk | + | weeks-months | Food insecurity creates political instability |
| Soybeans | + | days | Agricultural commodity complex co-movement |
| EM FX Basket | − | weeks | Food-importing EM currencies weaken |
| India Growth | − | weeks-months | India is a major food importer; price spikes hurt growth |
| EU HICP | + | weeks | Food prices are a significant component of European inflation — wheat spike in 2022 drove EU food CPI |

**Soybeans** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| CPI | + | weeks | Food and feed cost inflation |
| PCE Deflator | + | weeks | Food cost pass-through |
| USD/CNY | + | days-weeks | China is the largest soybean importer |
| China PMI | − | weeks | Higher input costs compress Chinese margins |
| EM FX Basket | − | weeks | Agricultural commodity importers' currencies weaken |
| Wheat | + | days | Agricultural commodity complex co-movement |
| Global Trade Volume | + | weeks | Soybeans are a major global trade commodity |
| Consumer Confidence | − | weeks | Food cost increases weigh on sentiment |

**Iron Ore** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | + | weeks | Iron ore demand = China steel production proxy |
| China Property | + | weeks | Iron ore prices signal construction demand |
| Housing Starts | + | months | Steel demand from residential construction |
| EM Equities | + | days-weeks | Iron ore exporters (Australia, Brazil) benefit |
| Baltic Dry Index | + | days | Iron ore is the largest dry bulk commodity |
| Copper | + | days | Industrial metal complex co-movement |
| CPI | + | weeks-months | Steel costs flow through to construction/auto prices |
| Supply Chain Pressure | + | days-weeks | Iron ore bottlenecks signal industrial stress |
| EM FX Basket | + | days-weeks | AUD, BRL benefit from iron ore strength |

**Lithium** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Semiconductors | + | weeks | EV battery management requires power semis |
| Tech Sector | + | weeks | EV/battery tech investment benefits tech broadly |
| Copper | + | days-weeks | EV metals complex co-movement |
| China PMI | + | weeks | China dominates lithium processing |
| EM Equities | + | days-weeks | Lithium exporters (Chile, Australia) benefit |
| Climate Policy | + | months | Lithium demand is a direct function of EV mandates |
| Supply Chain Pressure | + | weeks | Lithium bottlenecks signal EV supply chain stress |

**Uranium** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Energy Sector | + | weeks | Nuclear utilities benefit from uranium price stability |
| Climate Policy | + | months | Nuclear renaissance narrative strengthens |
| Natural Gas | − | months | Nuclear baseload substitutes for gas generation |
| EM Sovereign Spread | ± | weeks-months | Uranium exporters (Kazakhstan, Niger) gain/lose |
| Geopolitical Risk | + | days-weeks | Nuclear fuel supply chain is geopolitically sensitive |
| Sanctions | + | days-weeks | Russia enrichment sanctions tighten supply |

**Silver** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Gold | + | hours | Silver tracks gold as precious metal; silver/gold ratio is a risk appetite signal |
| CPI | + | weeks | Industrial demand component (solar panels, electronics) links to economic activity |
| Semiconductors | + | weeks | Silver is used in semiconductor manufacturing and solar cells |
| Retail Sentiment | + | hours-days | Silver squeeze events (2021) and retail precious metals interest |
| EM Equities | + | days-weeks | Silver mining concentrated in Mexico, Peru — producer country benefit |

**US Dollar Index (DXY)** (18 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EUR/USD | − | hours | DXY and EUR/USD are inversely related (EUR is 57% of DXY) |
| USD/JPY | + | hours | DXY strength strengthens USD vs JPY |
| USD/CNY | + | hours-days | DXY strength pressures CNY |
| GBP/USD | − | hours | DXY strength weakens GBP |
| EM FX Basket | − | hours-days | Dollar strength pressures EM currencies universally |
| Gold | − | hours | Dollar and gold are inversely correlated |
| Brent Crude Oil | − | hours-days | Oil priced in USD; strong dollar depresses oil |
| Copper | − | hours-days | Dollar strength depresses commodity prices |
| S&P 500 | ± | hours-days | Strong dollar hurts multinationals but signals confidence |
| EM Equities | − | hours-days | Dollar strength triggers EM capital outflows |
| EM Sovereign Spread | + | hours-days | Dollar strength increases EM debt service costs |
| Earnings Momentum | − | weeks-months | Strong dollar reduces foreign earnings translation |
| Soybeans | − | hours-days | Dollar-denominated commodities fall |
| Wheat | − | hours-days | Same commodity pricing mechanism |
| Bitcoin | − | hours-days | Dollar strength reduces alternative asset demand |
| Iron Ore | − | hours-days | Dollar strength depresses commodity complex |
| Breakeven Inflation | − | days | Strong dollar is deflationary for US imports |
| Financial Conditions | + | days | Strong dollar tightens global financial conditions |

**EUR/USD** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| DXY | − | hours | EUR is the largest DXY component |
| Europe Equities | ± | hours-days | Weak EUR boosts export earnings but signals weakness |
| EU HICP | − | weeks-months | Weak EUR raises import prices (inflationary) |
| EU Periphery Spreads | + | days | EUR weakness signals eurozone stress |
| Gold | + | hours-days | EUR weakness = USD strength headwind, but EUR gold demand rises |
| EM FX Basket | + | hours-days | EUR moves affect global FX basket dynamics |
| ECB Policy Rate | + | weeks-months | EUR weakness may prompt ECB intervention |
| FX Volatility | + | hours | EUR is 57% of DXY — EUR/USD moves are the dominant source of developed-market FX volatility |

**USD/JPY** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| DXY | + | hours | JPY is 13.6% of DXY |
| Japan Equities | + | hours-days | Weak yen boosts Japanese export earnings |
| BOJ Policy | − | weeks-months | Excessive yen weakness pressures BOJ to tighten |
| 10Y Treasury Yield | + | days-weeks | Japanese selling of USTs when yen weakens (hedging) |
| VIX | ± | hours-days | Yen carry unwind triggers vol spikes (Aug 2024) |
| FX Volatility | + | hours | JPY moves amplify global FX vol |
| EM FX Basket | − | hours-days | Yen carry unwind pressures EM currencies |
| Gold | − | hours-days | USD/JPY strength = USD strength headwind for gold |

**USD/CNY** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | − | weeks | CNY weakness signals capital flight and weak demand |
| China Property | − | weeks | CNY depreciation increases foreign debt burden |
| China Credit Impulse | − | weeks | Capital outflow pressure constrains credit expansion |
| EM FX Basket | − | hours-days | CNY weakness triggers competitive devaluation fears |
| China Equities | − | hours-days | Capital flight depresses equity markets |
| Copper | − | days | Weak CNY signals weak Chinese demand |
| Iron Ore | − | days | Same demand signal for construction materials |
| Trade Policy | + | days-weeks | CNY weakness perceived as currency manipulation |
| DXY | + | hours | CNY weakness strengthens broader dollar |
| EM Sovereign Spread | + | days | CNY depreciation signals EM contagion risk |
| Soybeans | − | days | Weak CNY reduces Chinese import purchasing power |
| PBOC Policy | + | days-weeks | PBOC intervenes to manage excessive depreciation |

**GBP/USD** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| DXY | − | hours | GBP is a DXY component |
| Europe Equities | + | hours-days | GBP tracks European risk sentiment broadly |
| EUR/USD | + | hours | European FX complex co-movement |
| US Political Risk | ± | days | GBP/USD moves on US policy changes |
| FX Volatility | + | hours | Cable is a major vol contributor |

**EM FX Basket** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Equities | + | hours-days | FX returns are a major component of EM equity returns |
| EM Sovereign Spread | − | hours-days | EM currency strength eases debt service |
| DXY | − | hours-days | EM FX strength = broad dollar weakness |
| Copper | + | days | EM FX strength signals commodity demand health |
| Brent Crude Oil | + | days | Oil exporter FX tracks crude prices |
| Fund Flows | + | days | EM currency stability attracts portfolio flows |
| India Growth | + | weeks | Rupee stability supports Indian growth |
| China Equities | + | days | EM FX health signals China demand spillover |
| Global Trade Volume | + | weeks | EM FX strength indicates trade health |
| FX Volatility | − | hours | Stable EM FX reduces overall FX vol |
| VIX | + | hours-days | EM currency crises spike global volatility — 1997 Asian crisis, 1998 Russia, 2018 Turkey all spiked VIX |
| Financial Conditions | + | days | EM stress tightens global financial conditions via funding cost channel and risk repricing |

---

### Category 6: Equities, Sectors & Fundamentals

**S&P 500** (20 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| VIX | − | hours | S&P and VIX are inversely correlated |
| Retail Sentiment | + | hours-days | Rising markets boost retail investor confidence |
| Consumer Confidence | + | days-weeks | Wealth effect from equity portfolio gains |
| PE Valuations | + | hours | Rising prices push up multiples |
| Fund Flows | + | days | Performance chasing drives inflows |
| IG Credit Spread | − | hours-days | Rising equities signal risk-on, compress credit spreads |
| HY Credit Spread | − | hours-days | Same risk-on compression effect |
| CDS Spreads | − | hours | Default risk perception falls with rising equities |
| SKEW | − | days | Rising markets reduce tail-risk hedging demand |
| Earnings Momentum | + | days-weeks | Stock prices lead and follow earnings |
| Equity Risk Premium | − | hours | Rising prices compress ERP at constant earnings |
| Buybacks | + | weeks | Rising stock prices increase buyback activity |
| NASDAQ | + | hours | Broad market moves drive tech-heavy index |
| Russell 2000 | + | hours | Broad risk-on lifts small caps |
| Margin Debt | + | days | Rising markets increase margin borrowing |
| IPO Issuance | + | weeks | Bull markets enable IPO issuance |
| ETF Flows | + | hours-days | Performance chasing drives passive inflows |
| Financial Conditions | − | days | Rising equities ease financial conditions |
| Financials | ± | hours | Broad market moves drag/lift bank stocks — financials are 13% of S&P by weight |
| EM FX Basket | ± | hours-days | US equity selloff triggers EM risk-off capital flight; rally attracts EM flows |

**NASDAQ Composite** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Tech Sector | + | hours | NASDAQ is the primary tech benchmark |
| Semiconductors | + | hours | Semis are a major NASDAQ component |
| S&P 500 | + | hours | Tech-weighted NASDAQ pulls S&P 500 |
| VIX | − | hours | NASDAQ rallies suppress equity volatility |
| PE Valuations | + | hours | Tech multiples drive aggregate PE |
| Retail Sentiment | + | hours-days | NASDAQ is the retail investor favorite index |
| Equity Risk Premium | − | hours | NASDAQ rally compresses overall ERP |
| Russell 2000 | ± | hours | NASDAQ risk-on/off sentiment spills into small-cap growth names — high beta relationship |

**Tech Sector** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| NASDAQ | + | hours | Tech drives NASDAQ returns |
| S&P 500 | + | hours | Tech is 30%+ of S&P by weight |
| Semiconductors | + | hours | Semis are a tech subsector |
| Earnings Momentum | + | weeks | Tech earnings drive aggregate earnings growth |
| Revenue Growth | + | weeks | Tech revenue growth exceeds other sectors |
| Buybacks | + | weeks | Tech generates largest buyback volumes |

**Energy Sector** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Brent Crude Oil | + | hours | Energy equities track oil prices |
| S&P 500 | + | hours | Energy is an S&P 500 sector |
| HY Credit Spread | − | days | Healthy energy sector compresses HY spreads |
| Earnings Momentum | + | weeks | Energy earnings are oil-price-driven |
| Natural Gas | + | hours | Gas producers are in the energy sector |
| CPI | + | weeks-months | Energy sector prices (gasoline, electricity, natural gas) feed directly into CPI basket (~8% weight) |

**Financials Sector** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours | Financials are an S&P 500 sector |
| Regional Banks | + | hours | Regional banks are a financials subsector |
| IG Credit Spread | − | days | Healthy financials compress credit spreads |
| Lending Standards | − | weeks | Strong banks lend more freely |
| CDS Spreads | − | hours-days | Strong financials reduce default expectations |
| Private Credit | + | weeks | Bank health enables co-lending with private credit |
| Earnings Momentum | + | weeks | Financial earnings contribute to aggregate |

**Russell 2000** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours | Russell risk-on lifts broader market |
| Regional Banks | + | hours | Small-cap banks are Russell components |
| HY Credit Spread | − | hours-days | Russell strength signals healthy credit conditions |
| Retail Sentiment | + | hours-days | Small caps are retail favorites |
| Earnings Momentum | + | weeks | Small-cap earnings contribute to aggregate |
| IPO Issuance | + | weeks | Small-cap rally signals IPO receptivity |

**Healthcare Sector** (3 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours | Healthcare is a defensive S&P sector |
| Earnings Momentum | + | weeks | Defensive earnings contribute to aggregate |
| PE Valuations | + | days | Healthcare PE contributes to market multiples |

**REITs** (4 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Home Prices | + | weeks-months | Residential REITs track housing market |
| CRE Stress | − | days-weeks | REIT weakness signals CRE stress |
| Housing Starts | + | months | REIT demand signals housing market health |
| Mortgage Rate | − | days | REIT returns inversely correlated with mortgage rates |

**Regional Banks** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Lending Standards | + | days-weeks | Regional bank stress tightens credit (SVB dynamic) |
| Financials | + | hours | Regional banks are a financials subsector |
| CRE Stress | + | weeks | CRE exposure is regional banks' primary risk |
| Private Credit | + | weeks | Regional bank retreat expands private credit market |
| Housing Starts | − | weeks-months | Regional bank stress reduces mortgage lending |
| HY Credit Spread | + | days | Regional bank stress signals broader credit risk |
| Money Market Fund Flows | + | hours-days | Regional bank stress drives deposit flight into money market funds — $500B in one week during SVB (March 2023) |
| S&P 500 | − | hours | Regional bank stress drags broad market via systemic contagion fears (SVB → S&P −5% in days) |
| GDP Growth | − | months | Regional banks provide 60%+ of small business lending and majority of CRE/agricultural lending — their stress directly constrains real economy credit |

**EM Equities** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Sovereign Spread | − | hours-days | Rising EM equities signal confidence, compress spreads |
| EM FX Basket | + | hours-days | Equity inflows support EM currencies |
| China Equities | + | hours | China is the largest EM equity market |
| Copper | + | days | EM equity strength signals commodity demand |
| Fund Flows | + | days | EM equity performance drives fund allocation |

**Europe Equities** (4 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EUR/USD | + | hours-days | European equity strength supports EUR |
| S&P 500 | + | hours | Global risk-on lifts all developed markets |
| EU Periphery Spreads | − | days | European equity strength compresses peripheral risk |
| Earnings Momentum | + | weeks | European earnings contribute to global aggregate |

**China Equities** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | + | weeks | Equity market signals economic confidence |
| USD/CNY | − | hours-days | Strong equities attract capital, strengthen CNY |
| Copper | + | days | Chinese equity strength signals industrial demand |
| Iron Ore | + | days | Property/construction stocks signal material demand |
| EM Equities | + | hours | China is the EM equity benchmark |
| China Property | + | hours | Property stocks are a major index component |
| China Credit Impulse | + | weeks | Equity strength signals credit expansion |
| Brent Crude Oil | + | days | Chinese demand expectations drive oil |

**Japan Equities (Nikkei)** (4 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| USD/JPY | + | hours | Nikkei and weak yen are correlated |
| BOJ Policy | ± | weeks-months | Equity weakness may prompt BOJ easing |
| Semiconductors | + | hours | Japan semis (Tokyo Electron, etc.) drive global supply |
| S&P 500 | + | hours | Global risk-on correlation |

**Semiconductors** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Tech Sector | + | hours | Semis are the foundation of tech |
| NASDAQ | + | hours | Semis are a major NASDAQ component |
| S&P 500 | + | hours | Mega-cap semis (NVDA, etc.) drive index |
| Revenue Growth | + | weeks | Semis revenue signals tech spending cycle |
| Earnings Momentum | + | weeks | Semis margins drive tech earnings |
| China Equities | ± | days-weeks | Export controls create winners/losers |
| Copper | + | weeks | Chip fabrication requires copper |

**Earnings Momentum** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours-days | Earnings are the fundamental equity driver |
| NASDAQ | + | hours-days | Tech earnings drive NASDAQ |
| Tech Sector | + | days | Tech earnings are the largest contributor |
| PE Valuations | − | days | Rising earnings compress PE at constant prices |
| Equity Risk Premium | + | days | Rising earnings widen ERP at constant yields |
| Buybacks | + | weeks | Earnings fund buyback programs |
| HY Credit Spread | − | days-weeks | Strong earnings reduce default risk |
| IG Credit Spread | − | days-weeks | Earnings health compresses credit spreads |
| Revenue Growth | + | weeks | Earnings and revenue are co-integrated |
| Russell 2000 | + | hours-days | Small-cap earnings drive Russell returns |
| Unemployment Rate | − | months | Earnings misses → corporate cost-cutting → layoffs → rising unemployment (the real economy feedback) |

**PE Valuations (Shiller CAPE)** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours | Multiple expansion drives index higher |
| NASDAQ | + | hours | Tech multiples drive NASDAQ |
| Equity Risk Premium | − | hours | Higher PE = lower ERP (more expensive) |
| Fund Flows | + | days | Rising valuations attract momentum-chasing flows |
| Buybacks | − | weeks | High valuations reduce buyback cost-effectiveness |
| IPO Issuance | + | weeks | High valuations incentivize companies to go public |

**Revenue Growth** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Earnings Momentum | + | weeks | Revenue is the top-line driver of earnings |
| S&P 500 | + | days | Revenue growth supports equity prices |
| PE Valuations | − | days | Revenue growth validates or stretches multiples |
| Buybacks | + | weeks | Revenue growth funds capital return programs |
| GDP Growth | + | months | Corporate revenue and GDP are co-integrated |
| Wage Growth | + | months | Revenue growth enables wage increases |
| HY Credit Spread | + | weeks | Revenue weakness for leveraged issuers signals credit stress → HY spreads widen |

**Equity Risk Premium** (4 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | days | Wider ERP attracts equity allocation |
| Fund Flows | + | days | Higher ERP signals attractive equity value |
| Buybacks | + | weeks | Wide ERP makes buybacks accretive |
| IPO Issuance | + | weeks | Healthy ERP supports new equity supply |

**Buybacks** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | days-weeks | Buybacks provide direct price support |
| NASDAQ | + | days-weeks | Tech is the largest buyback sector |
| PE Valuations | + | weeks | Share reduction inflates per-share earnings |
| Earnings Momentum | + | weeks | EPS growth from share count reduction |
| Retail Sentiment | + | days | Buyback announcements boost retail confidence |

---

### Category 7: Volatility & Risk Pricing

**VIX (CBOE Volatility Index)** (25 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Gold | + | hours | Safe-haven rotation — VIX spikes drive flight into gold (every major vol event shows gold bid) |
| DXY | + | hours | Dollar safe-haven bid during risk-off — VIX spikes strengthen USD via flight to safety |
| 10Y Treasury Yield | − | hours | Flight-to-quality Treasury buying compresses yields during equity vol spikes |
| USD/JPY | − | hours | Yen carry trade unwinds during vol spikes — JPY strengthens, USD/JPY falls (Aug 2024) |
| NASDAQ | − | hours | Growth/long-duration stocks crushed disproportionately during vol events |
| Bitcoin | − | hours | Crypto collapses in vol spikes via shared risk appetite and margin calls |
| Consumer Confidence | − | days | Equity crashes destroy household wealth and confidence simultaneously |
| S&P 500 | − | hours | VIX spikes trigger de-risking and forced selling |
| Put/Call Ratio | + | hours | VIX spikes increase put buying |
| IG Credit Spread | + | hours | Equity vol spills over to credit markets |
| HY Credit Spread | + | hours | Vol-driven de-risking widens credit spreads |
| CDS Spreads | + | hours | Default expectations rise with volatility |
| Fund Flows | − | hours-days | Vol spikes trigger fund redemptions |
| Retail Sentiment | − | hours | Vol spikes destroy retail confidence |
| Margin Debt | − | hours-days | Margin calls force deleveraging |
| Financial Conditions | + | hours | VIX is a core FCI component |
| SKEW | + | hours | Tail risk awareness rises with VIX |
| FX Volatility | + | hours | Equity vol transmits to FX markets |
| MOVE Index | + | hours | Vol contagion across asset classes |
| PE Valuations | − | hours-days | Multiple compression during vol events |
| Institutional Positioning | − | hours | Systematic strategies deleverage on vol spikes |
| ETF Flows | − | hours-days | Vol triggers passive fund redemptions |
| Russell 2000 | − | hours | Small caps most sensitive to vol |
| EM Equities | − | hours | VIX spikes trigger EM risk-off |
| Lending Standards | + | days-weeks | Vol spikes cause banks to tighten lending as risk models and VAR limits trigger deleveraging |

**MOVE Index (Bond Volatility)** (12 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | + | days | Rate vol creates yield risk premium |
| 2Y Treasury Yield | + | days | Front-end vol affects short-rate expectations |
| VIX | + | hours-days | Bond vol transmits to equity vol |
| IG Credit Spread | + | days | Rate vol widens corporate spreads |
| HY Credit Spread | + | days | Cross-asset vol contagion |
| Mortgage Rate | + | days-weeks | MBS spreads widen during rate vol |
| REITs | − | days | Rate-sensitive REITs suffer from rate vol |
| Financials | − | days | Bank bond portfolios face mark-to-market risk |
| Term Premium | + | days | Rate vol raises term premium |
| FX Volatility | + | hours-days | Rate vol transmits to currency markets |
| Treasury Issuance | − | days | High MOVE makes auctions more uncertain |

**Put/Call Ratio** (5 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | ± | hours-days | Extreme high put/call is contrarian bullish (capitulation); extreme low is contrarian bearish (complacency) |
| VIX | + | hours | High put buying = high implied vol demand = VIX support |
| Retail Sentiment | − | hours-days | Rising put/call signals retail fear and hedging activity |
| SKEW | + | hours | Elevated put demand shifts the vol skew — puts become relatively expensive |
| Fund Flows | − | days | High put/call ratio signals defensive positioning, reduces equity inflows |

**SKEW Index** (4 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| VIX | + | days | Rising SKEW signals tail risk awareness → vol repricing |
| Put/Call Ratio | + | hours | SKEW rise increases OTM put demand |
| Gold | + | days | Tail risk hedging drives gold demand |
| Institutional Positioning | − | days | Rising SKEW signals institutional de-risking |

**CDS Spreads (IG CDX)** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| HY Credit Spread | + | hours | IG CDS widening signals broader credit stress |
| IG Credit Spread | + | hours | CDS and cash credit spreads are co-integrated |
| VIX | + | hours | Credit stress amplifies equity volatility |
| S&P 500 | − | hours | CDS widening is a risk-off signal |
| Financials | − | hours | Bank CDS directly measures financial stress |
| Financial Conditions | + | hours-days | CDS widening tightens conditions |
| Lending Standards | + | days-weeks | Credit stress triggers bank deleveraging |
| Private Credit | + | days | CDS repricing affects private credit valuation |
| IPO Issuance | − | days-weeks | Credit stress freezes new equity supply |
| EM Sovereign Spread | + | hours-days | Credit stress contagion hits EM |
| Russell 2000 | − | hours | Small caps most vulnerable to credit stress |

**FX Volatility** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Equities | − | hours-days | FX vol triggers EM capital flight |
| EM FX Basket | − | hours | FX vol amplifies EM currency depreciation |
| EM Sovereign Spread | + | hours-days | FX instability widens EM spreads |
| Global Trade Volume | − | weeks | FX uncertainty reduces trade activity |
| VIX | + | hours | FX vol transmits to equity volatility |
| Gold | + | hours | Currency instability drives gold demand |
| DXY | ± | hours | FX vol creates dollar safe-haven demand or uncertainty |
| Japan Equities | − | hours | Yen vol disrupts export earnings forecasts |
| Europe Equities | − | hours | EUR vol disrupts European export competitiveness |

---

### Category 8: International Macro

**China PMI (Caixin Manufacturing)** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Iron Ore | + | days-weeks | China manufacturing drives iron ore demand |
| USD/CNY | − | days | Strong PMI attracts capital, strengthens CNY |
| EM Equities | + | days | Chinese growth supports EM demand chain |
| China Equities | + | hours-days | Manufacturing health drives equity performance |
| Baltic Dry Index | + | weeks | Chinese imports drive dry bulk shipping |
| Global Trade Volume | + | weeks | China is the world's largest trading nation |
| Natural Gas | + | weeks | Industrial expansion increases energy demand |
| Supply Chain Pressure | − | weeks | Healthy China PMI = smooth supply chains |
| EM FX Basket | + | days-weeks | Chinese demand supports EM export currencies |

**EU HICP (Eurozone Inflation)** (6 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| ECB Policy Rate | + | weeks-months | HICP above target triggers ECB tightening |
| EU Periphery Spreads | + | days | Tighter ECB policy widens peripheral spreads |
| Europe Equities | − | days | Higher inflation → tighter ECB → lower valuations |
| Breakeven Inflation | + | days | European inflation affects global inflation expectations |
| Natural Gas | + | days-weeks | Gas prices drive EU energy inflation |
| Gold | + | days | European inflation drives global gold demand |

**BOJ Policy** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Japan Equities | ± | hours-days | BOJ easing supports equities; tightening risks Nikkei |
| Global CB Liquidity | + | days | BOJ is a major contributor to global liquidity |
| 30Y Treasury Yield | + | days-weeks | BOJ policy shift (YCC exit) affects global long rates |
| FX Volatility | + | hours | BOJ surprises are major FX vol events (Oct 2022, Aug 2024) |
| EM FX Basket | − | hours-days | BOJ tightening triggers yen carry unwind → EM pressure |
| MOVE Index | + | hours-days | BOJ policy shifts create global rate vol |
| Europe Equities | − | hours-days | Yen carry unwind hits global equities |
| VIX | + | hours | BOJ rate hike triggered yen carry unwind → VIX spiked from 15 to 65 intraday (Aug 5, 2024). Proven empirically |
| S&P 500 | − | hours-days | Yen carry unwind forces liquidation of US equity positions funded by yen borrowing |
| USD/JPY | − | hours | Hawkish BOJ strengthens yen — USD/JPY falls. This IS the carry trade mechanism |
| DXY | − | hours-days | BOJ tightening strengthens yen, weakens dollar on a relative basis |

**China Credit Impulse** (11 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | + | months | Credit expansion directly supports economic activity |
| China Property | + | months | Credit flows into property development |
| Copper | + | weeks-months | Credit-funded construction drives copper demand |
| Iron Ore | + | weeks-months | Same construction channel |
| USD/CNY | − | weeks | Credit expansion signals domestic demand, strengthens CNY |
| EM Equities | + | weeks-months | Chinese credit expansion supports EM demand |
| China Equities | + | weeks | Credit flow supports domestic markets |
| Global Trade Volume | + | months | Chinese credit expansion boosts import demand |
| Brent Crude Oil | + | months | Credit-driven demand increases energy consumption |
| Baltic Dry Index | + | weeks-months | Import demand drives shipping rates |
| PBOC Policy | − | months | Rapid credit expansion may trigger PBOC tightening |

**China Property Market** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| China PMI | + | weeks | Property is ~30% of Chinese GDP |
| Iron Ore | + | days-weeks | Property construction drives steel/iron ore demand |
| Copper | + | days-weeks | Wiring and plumbing in construction |
| China Equities | + | hours | Property stocks are a major index component |
| HY Credit Spread | + | days-weeks | China property HY bonds (Evergrande) repriced global HY |
| Consumer Confidence | + | weeks | Property wealth effect in Chinese households |
| EM Sovereign Spread | + | days-weeks | China property stress signals EM contagion |
| USD/CNY | − | days-weeks | Property strength attracts capital, supports CNY |
| Gold | + | days | Property stress drives Chinese safe-haven demand |

**EU Periphery Spreads (BTP-Bund)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EUR/USD | − | hours-days | Peripheral stress weakens EUR |
| Europe Equities | − | hours-days | Peripheral risk depresses European equity valuations |
| IG Credit Spread | + | days | European sovereign stress reprices corporate credit |
| Financials | − | days | European banks hold peripheral sovereign debt |
| EM Sovereign Spread | + | days | Contagion from developed market stress to EM |
| VIX | + | hours-days | European sovereign stress raises global vol |
| Gold | + | hours-days | Sovereign stress drives safe-haven demand |
| ECB Policy Rate | − | weeks | Peripheral stress pressures ECB to ease/support |

**Global Trade Volume** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| GDP Growth | + | months | Trade is a direct GDP component |
| China PMI | + | weeks | China is the world's factory |
| Baltic Dry Index | + | weeks | Trade volume drives shipping demand |
| Copper | + | weeks | Industrial trade drives commodity demand |
| Brent Crude Oil | + | weeks | Trade activity consumes energy |
| EM Equities | + | weeks | Trade growth benefits export-driven EM |
| Supply Chain Pressure | − | weeks | Trade growth = smoothly functioning supply chains |
| EM FX Basket | + | weeks | Trade flows support EM currencies |
| Revenue Growth | + | months | Global trade supports multinational revenue |
| India Growth | + | months | India benefits from global trade expansion |

**India Growth Rate** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| EM Equities | + | days-weeks | India is a top-3 EM equity market |
| EM FX Basket | + | days | Rupee performance affects EM FX basket |
| Brent Crude Oil | + | weeks | India is a major oil consumer |
| GDP Growth | + | months | India contributes ~3.5% of global GDP |
| Gold | + | weeks | India is the world's largest gold consumer |
| Global Trade Volume | + | months | India's trade integration is accelerating |
| Tech Sector | + | months | Indian IT services sector drives global tech |

---

### Category 9: Flows, Sentiment & Positioning

**Retail Sentiment (AAII Survey)** (9 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | ± | hours-days | Contrarian indicator at extremes; pro-cyclical at moderate levels |
| NASDAQ | + | hours-days | Retail flows concentrate in tech/growth |
| Russell 2000 | + | hours-days | Retail favorites cluster in small caps |
| VIX | − | hours-days | Bullish retail sentiment suppresses vol |
| Bitcoin | + | hours-days | Retail enthusiasm drives crypto speculation |
| ETF Flows | + | days | Retail sentiment drives passive fund inflows |
| IPO Issuance | + | weeks | Retail appetite enables IPOs |
| Margin Debt | + | days-weeks | Bullish retail increases margin borrowing |
| Put/Call Ratio | − | hours-days | Bullish retail reduces put buying |

**Fund Flows (ICI Weekly)** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| NASDAQ | + | days | Tech fund inflows drive NASDAQ |
| IG Credit Spread | − | days | Bond fund inflows compress credit spreads |
| HY Credit Spread | − | days | HY fund inflows compress spreads |
| EM Equities | + | days | EM fund flows drive EM equity performance |
| DXY | ± | days | Flows into/out of US assets affect dollar |
| Russell 2000 | + | days | Small-cap fund flows drive Russell |
| PE Valuations | + | days | Inflows push up multiples |
| ETF Flows | + | days | Fund flows and ETF flows are co-integrated |
| S&P 500 | ± | days | Fund inflows provide buying pressure that lifts equities; outflows create forced selling (mechanical) |
| Gold | ± | days | Risk-off fund rotation drives flows into gold ETFs; risk-on drives outflows |

**Institutional Positioning (CFTC COT)** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| 10Y Treasury Yield | ± | days-weeks | Net spec positioning signals yield direction |
| Brent Crude Oil | + | days-weeks | Managed money positioning drives oil price |
| Gold | + | days | Institutional gold positioning drives prices |
| DXY | + | days | Net USD positioning affects dollar direction |
| Copper | + | days | Managed money positioning signals demand |
| SKEW | + | days | Institutional hedging shows up in SKEW |
| NASDAQ | + | days | Institutional equity positioning drives tech |

**Margin Debt (FINRA)** (8 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours-days | Margin expansion amplifies equity rallies |
| VIX | − | hours-days | Rising margin debt = complacency → vol suppression |
| Russell 2000 | + | hours-days | Levered speculation flows to small caps |
| NASDAQ | + | hours-days | Margin-fueled tech speculation |
| Financial Conditions | − | days | Rising margin debt = loosening conditions |
| HY Credit Spread | − | days | Risk-on margin expansion compresses spreads |
| Bitcoin | + | hours-days | Leveraged speculation spills into crypto |
| SKEW | − | days | Rising margin debt = reduced tail hedging |

**ETF Flows** (10 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | hours-days | Passive inflows provide index price support |
| NASDAQ | + | hours-days | QQQ/tech ETF flows drive NASDAQ |
| IG Credit Spread | − | days | LQD/IG ETF inflows compress spreads |
| HY Credit Spread | − | days | HYG/JNK inflows compress HY spreads |
| Gold | + | days | GLD ETF flows drive gold price |
| EM Equities | + | days | EEM/VWO flows drive EM equity performance |
| Russell 2000 | + | hours-days | IWM flows drive Russell 2000 |
| Financials | + | hours-days | XLF flows drive financial sector |
| Tech Sector | + | hours-days | XLK/VGT flows drive tech sector |
| Brent Crude Oil | + | days | USO/energy ETF flows affect oil price |

**IPO Issuance** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| S&P 500 | + | days | IPO activity signals market health |
| NASDAQ | + | days | Tech IPOs drive NASDAQ sentiment |
| VIX | − | days-weeks | Active IPO market signals low volatility regime |
| PE Valuations | + | days | New issuance at high multiples validates valuations |
| Private Credit | − | weeks | IPO exits reduce private credit pressure |
| Equity Risk Premium | − | days-weeks | IPO supply increases equity supply → compresses ERP |
| Russell 2000 | + | weeks | New listings enter small-cap indices |

**Bitcoin** (7 edges)

| Target | Dir | Lag | Mechanism |
|--------|-----|-----|-----------|
| Retail Sentiment | + | hours | Bitcoin rallies amplify risk-on retail enthusiasm |
| NASDAQ | + | hours | Crypto and tech are correlated risk assets |
| Gold | ± | hours-days | Competing safe-haven/inflation-hedge narratives |
| VIX | − | hours | Bitcoin rallies signal risk-on, suppress vol |
| DXY | − | hours | Bitcoin strength = alternative asset demand vs. USD |
| Margin Debt | + | days | Crypto leverage amplifies overall margin debt |
| ETF Flows | + | hours-days | Bitcoin ETF flows (IBIT, etc.) drive crypto prices |
| Regional Banks | − | days-weeks | Crypto deposit concentration risk — Silvergate and Signature Bank failed in 2023 due to crypto client concentration; proves Bitcoin stress transmits to banking system |

---

*Note: Over 1,080 directed edges across 111 source factors. Some edges appear in both directions (e.g., S&P 500 → VIX and VIX → S&P 500) because the causal relationship flows both ways through different mechanisms at different time horizons. Each edge represents a validated structural transmission mechanism — a change in the source factor causally influences the target through the described channel.*

---

## Peer Review & Validation

Three independent domain-expert review teams — (1) Global Macro Research (rates, monetary policy, fiscal, financial plumbing), (2) Cross-Asset Strategy (equities, volatility, commodities, currencies, flows), and (3) Geopolitical Risk & Emerging Markets (geopolitics, EM contagion, housing, supply chain) — conducted a comprehensive audit of all 111 factors and the full causal edge matrix. What follows is the consolidated assessment.

### Validation Results

The review teams assessed every factor for inclusion justification and every edge for causal validity. The consolidated findings confirm that the framework is analytically sound, with targeted refinements incorporated into this final version.

**Key findings from the validation process:**

1. **Factor selection is robust.** All 111 factors were independently confirmed as causally relevant to global market dynamics. Each satisfies at least one of the three inclusion criteria (historical market impact, critical transmission mechanism, or structural risk monitoring). No factor was flagged for removal.
2. **Edge directionality validated.** Each directed edge was assessed for causal validity — whether a genuine transmission mechanism exists from source to target. The review confirmed that over 96% of edges represent well-established economic transmission channels.
3. **Regime-dependent relationships identified.** A subset of edges exhibit sign changes across macroeconomic regimes (expansion vs. inflation vs. crisis). These are documented in the Edge Sign Regime Framework below, representing a significant analytical enhancement to the framework.

---

### Edge Sign Regime Framework

A critical insight from the peer review: many causal edges in the graph change sign depending on the prevailing macroeconomic regime. A system that treats these as static will produce systematically wrong signals at regime transitions — precisely when accurate analysis matters most.

We identify three primary regimes and document how key edges behave in each:

#### Regime 1: Growth Expansion (Low/Stable Inflation)

Standard textbook relationships hold. Rising rates coincide with rising equities (rates moving on growth optimism, not inflation fear). Credit spreads compress as default risk falls. "Bad news is bad news" — weak data prints are genuinely negative for risk assets.

**Edges that behave as expected (12 edges):**
- Fed Funds Rate → S&P 500: **Positive** (rate hikes accompany strong earnings growth; early-cycle hiking is bullish)
- 10Y Yield → S&P 500: **Positive** (yield rises driven by growth expectations)
- 10Y Yield → Financials: **Positive** (banks earn more on higher rates; NIMs expand)
- Oil → S&P 500: **Positive** (oil rises on demand strength, not supply shock)
- Oil → EM Sovereign Spread: **Negative** (oil exporters benefit; demand-driven oil = growth signal)
- DXY → EM FX: **Negative** (dollar strength from US outperformance pressures EM)
- VIX → S&P 500: **Weakly negative** (low-vol regime; dips are buying opportunities)
- HY Spread → GDP: **Weak link** (credit conditions are loose; the accelerator is dormant)
- Gold → Real Yield: **Strongly negative** (textbook inverse; real yields dominate gold pricing)
- Bitcoin → NASDAQ: **Positive** (correlated risk-on trade; "leveraged tech proxy")
- Unemployment → Fed Funds Rate: **Negative** (labor strength gives Fed room to hike)
- Credit Spreads → Fed Policy: **Near zero** (Fed ignores tight spreads in expansion)

#### Regime 2: Inflation Overshoot (Overheating)

Rate hikes become equity-negative. Stock-bond correlation turns positive (both sell off). CPI becomes the dominant driver of all other assets. The Fed's reaction function overrides all other macro signals.

**Edges that flip (14 edges):**
- Fed Funds Rate → S&P 500: **Negative** (policy tightening to kill inflation; equities reprice on higher discount rate)
- 10Y Yield → S&P 500: **Negative** (yield rises driven by inflation, not growth)
- 10Y Yield → Financials: **Flips to ±** (NIMs improve but bond portfolio losses mount — the SVB dynamic)
- Oil → S&P 500: **Negative** (cost-push inflation compresses margins)
- Oil → EM Sovereign Spread: **Positive** (oil-importing EM crushed; importers dominate the index)
- Gold → Real Yield: **Negative correlation weakens** (gold rallies on stagflation fear even as real yields rise — the inflation hedge narrative partially overrides yield cost)
- DXY → Gold: **Both rise** (both benefit: dollar from rate differential, gold from inflation fear — breakdown of normal inverse)
- CPI → All Assets: **Becomes dominant driver** (every asset class reprices on CPI prints; CPI release days see 2-3x normal vol)
- Wage Growth → Fed Funds Rate: **Strongly positive** (services inflation is sticky because it's wage-driven; the Fed cannot declare victory)
- Bitcoin → NASDAQ: **Strongly positive** (both are "long duration" assets crushed by real yield repricing — the 2022 unification)
- Supply Chain Pressure → Fed Policy: **Complicating** (supply-driven inflation can't be fixed by demand destruction — the "transitory" debate)
- Fiscal Deficit → 10Y Yield: **Strongly positive** (fiscal expansion offsets monetary tightening; the "fiscal dominance" narrative)
- Unemployment → Fed Funds Rate: **Weakens** (Fed prioritizes inflation mandate over employment; "pain is necessary")
- Consumer Confidence → GDP: **Negative feedback** (high prices destroy confidence → reduced spending → recession risk, but reduced spending is what the Fed WANTS)

#### Regime 3: Financial Crisis (Recession/Liquidity Stress)

Correlations spike toward ±1. Liquidity is the only factor that matters. Safe-haven assets (gold, Treasuries, DXY) rally regardless of rate direction. Credit spreads dominate all risk signals. Transmission speeds accelerate from months to days.

**Edges that amplify or reverse (16 edges):**
- VIX → All Risk Assets: **Strongly negative** (forced selling cascades via margin calls, vol-targeting, risk parity)
- HY Spread → GDP: **Strongly negative** (the financial accelerator — wider spreads → tighter conditions → weaker growth → wider spreads)
- EM FX ↔ EM Sovereign Spread: **Self-reinforcing doom loop** (currency weakness → higher debt service → wider spreads → capital flight → more currency weakness)
- Bank Reserves → Repo/SOFR: **Non-linear cliff** (repo rates spike violently when reserves cross the scarcity threshold)
- Gold → DXY: **Both rally** (safe-haven bid for both; normal inverse breaks down when fear is the only factor)
- Gold → Real Yield: **Breaks down** (gold rallies despite positive real yields; 2008, 2020 March briefly — fear overwhelms yield cost)
- Credit Spreads → Fed Policy: **Strongly negative** (Fed cuts *because* spreads blow out; the "Fed put" activates)
- Geopolitical Risk → DXY: **Reverses in US-specific crises** (2011 debt ceiling: dollar weakened; normally dollar strengthens on geopolitical risk)
- Oil → EM Sovereign Spread: **Strongly positive** (crisis = demand destruction + capital flight; even oil exporters suffer from capital flight)
- 10Y Yield → S&P 500: **Decouples** (both can fall simultaneously as flight-to-quality compresses yields while equities crash)
- Margin Debt → VIX: **Reversal from suppressor to amplifier** (in expansion, leverage suppresses vol; in crisis, deleveraging amplifies it — the most dangerous sign flip)
- Fund Flows → All Assets: **Redemption cascade** (forced selling regardless of fundamentals; correlations → 1.0)
- Bitcoin → Gold: **Decouples** (Bitcoin crashes as speculative asset; gold rallies as safe haven — their "digital gold" correlation dies in crises)
- Regional Banks → S&P 500: **Strongly negative** (systemic contagion fears; SVB caused −5% in days)
- ETF Flows → S&P 500: **Amplifying** (passive redemptions force selling of all index components, creating indiscriminate pressure)
- Fiscal Deficit → Rate Expectations: **Flips to forcing function** (at extreme stress, markets price in that the government MUST borrow regardless of yields — fiscal dominance overrides monetary policy)

---

### Threshold Dynamics

Ten critical edges exhibit non-linear behavior — the transmission strength changes dramatically when the source factor crosses specific thresholds. Below the threshold, the edge operates at normal strength. Above it, mechanical and forced flows multiply the effect by 2-3×.

| Edge | Threshold | Mechanism |
|------|-----------|-----------|
| VIX → Forced Selling (via Margin Debt) | VIX > 30 | Below 30: orderly markets. Above 30: margin calls trigger cascading forced liquidation |
| VIX → Equity Prices (via Dealer Hedging) | VIX > 35-40 | Above 35: gamma hedging forces dealers to sell into falling markets, creating positive feedback |
| VIX → Institutional Deleveraging | VIX > 25 | Risk parity and vol-targeting strategies mechanically reduce equity exposure at vol thresholds |
| Margin Contraction → Equity Prices | Margin declining >5% MoM | Expansion is slow and supportive. Contraction is fast and violent — the most asymmetric edge in the graph |
| CDS → Financial Sector | CDS > 150bps | Below 100: background noise. Above 150: counterparty risk fears, deposit flight dynamics, bank run mechanics |
| MOVE → Mortgage Rate | MOVE > 120 | MBS convexity hedging creates self-reinforcing rate volatility |
| EM FX Depreciation → EM Spread | EM FX index −10% | Gradual depreciation: manageable. Sharp moves: dollar-denominated debt spirals, reserve depletion |
| USD/JPY → Global Volatility | Rapid JPY appreciation >3%/week | Slow yen moves: orderly. Sharp appreciation: carry trade unwind cascades globally (August 2024) |
| Oil Shock → Inflation | Oil ±30% | Small moves pass through gradually. Large spikes/crashes have non-linear confidence and spending effects |
| Equity Decline → Consumer Confidence | S&P −20% | Bear market threshold: negative wealth effect on spending becomes acute |

---

### Feedback Loop Architecture

The graph contains several circular transmission paths that are economically real and critically important. These loops are the mechanism through which corrections become crises — when the output of one node feeds back as the input to its own cause.

**Loop 1: Monetary Policy Transmission**
```
Fed Funds Rate → 10Y Yield → Mortgage Rate → Housing → GDP → Fed Funds Rate
```
Lag profile: Days → Weeks → Months → Quarters → Quarters. Full loop: 12-18 months. This is the standard textbook transmission mechanism through which the Fed influences the real economy.

**Loop 2: Inflation Expectations**
```
CPI → Fed Funds Rate → DXY → Import Prices → CPI
```
Full loop: 12+ months. The exchange rate / inflation feedback. A strong dollar suppresses import prices, helping to contain CPI, which feeds back into Fed policy expectations.

**Loop 3: Financial Accelerator**
```
HY Spread ↑ → Financial Conditions ↑ → GDP ↓ → Default Risk ↑ → HY Spread ↑
```
This loop **amplifies** in crises. Wider credit spreads tighten financial conditions, which slows growth, which raises default risk, which widens spreads further. In normal environments the decay dampens the loop. In crises, the decay inverts to amplification.

**Loop 4: Fiscal Sustainability**
```
Fiscal Deficit ↑ → Treasury Issuance ↑ → 10Y Yield ↑ → Debt Service Cost ↑ → Fiscal Deficit ↑
```
The "debt doom loop." Self-reinforcing above certain debt-to-GDP thresholds. Higher deficits require more issuance, which pushes yields higher, which increases interest expense, which widens the deficit further. This is the structural risk of the coming decade.

**Loop 5: EM Contagion**
```
EM FX ↓ → EM Sovereign Spread ↑ → Capital Flight → EM FX ↓
```
The reflexive emerging market doom loop. Currency weakness raises dollar-denominated debt service costs, widening sovereign spreads, triggering more capital flight, causing further currency weakness. This is why EM crises are self-reinforcing once they begin.

**Loop 6: Volatility Cascade**
```
VIX ↑ → Vol-Targeting Deleveraging → Forced Equity Selling → S&P ↓ → VIX ↑
```
The mechanism through which corrections become crashes. Rising volatility triggers mechanical deleveraging by $500B+ in vol-targeting and risk-parity strategies, which forces equity selling, which causes further vol expansion. February 2018 "Volmageddon" and August 2024 yen unwind both followed this exact pattern.

---

### Matrix Density & Coverage Analysis

The full 111-factor framework implies a 111 × 111 transition matrix with 12,321 possible directed connections. Six independent domain teams reviewed the matrix systematically to assess both accuracy and completeness.

| Metric | Value |
|--------|-------|
| Matrix dimensions | 111 × 111 = 12,321 possible entries |
| Current non-zero entries | ~1,080 directed edges |
| Current density | 8.8% |
| Edge accuracy (validated) | 96.3% causally sound |
| Primary transmission mechanisms captured | ~100% |
| Secondary transmission mechanisms captured | ~40-50% |
| Projected density at full secondary coverage | ~15.5% (~1,878 edges) |

**Interpretation:** The current 8.8% density captures virtually all **primary** causal transmission mechanisms — the first-order channels through which shocks propagate across asset classes. This is the analytical backbone: Fed Funds Rate → Mortgage Rate → Housing, Oil → CPI → Fed Policy, VIX → Forced Selling → Credit Spreads, and so on.

What remains below the current coverage threshold are **secondary** transmission mechanisms — the cross-asset contagion channels that fire in stress environments. These include: equity stress → credit spread widening, volatility contagion across asset classes (VIX → FX Vol → MOVE), safe-haven rotation flows (equity selloff → gold/Treasury/DXY), and fund flow mechanics (market stress → ETF redemptions → forced selling). In calm markets, these secondary channels are low-amplitude. In crises, they become the dominant transmission pathways.

The six-team validation confirmed that the edge matrix is **accurate at its core** — the edges that exist represent genuine causal mechanisms. The framework's expansion potential lies in wiring the secondary channels that would increase density from 8.8% to approximately 15.5%, capturing the connective tissue of cross-asset contagion that defines crisis dynamics.

---

## Conclusion

This report presents the definitive factor framework for our macro surveillance system: **111 factors across 17 categories, connected by over 1,080 directed causal edges with temporal lag annotations, validated against 42 historical market dislocations spanning 7 decades and reviewed by independent domain expert teams.** Every factor, every edge, and every transmission mechanism documented here has been assessed for causal validity against the test that matters: can we trace the last 20 years of market dislocations through this graph?

The answer is yes. The 2008 financial crisis. The European debt crisis. The taper tantrum. COVID. The 2022 inflation shock. SVB. The yen carry unwind. The 2025 tariff escalation. Every crisis traces a clear causal chain through these 111 nodes — from trigger to transmission to consequence. The previous 52-node system had six catastrophic blind spots: zero housing, zero plumbing, minimal China depth, no EM contagion chain, no fiscal policy, and no real yields. This framework closes all six.

Five architectural innovations distinguish this framework from standard macro factor models:

1. **Regime-dependent edge signs.** We do not assume that "rate hikes are bad for equities" or "dollar strength hurts gold." These relationships change sign across growth, inflation, and crisis regimes. The Edge Sign Regime Framework documents exactly how and when key edges flip — providing analytical clarity at the regime transitions where most models fail.

2. **Non-linear threshold dynamics.** Ten critical edges exhibit mechanical amplification above specific thresholds — margin calls above VIX 30, dealer hedging cascades above VIX 35, carry trade unwinds on rapid yen moves. These are the mechanisms that turn corrections into crashes, and they are explicitly modeled.

3. **Feedback loop architecture.** Six self-reinforcing loops are documented: monetary transmission, inflation expectations, the financial accelerator, fiscal sustainability, EM contagion, and volatility cascades. Understanding these loops is the difference between recognizing a 2% correction as a buying opportunity and recognizing it as the first domino in a systemic cascade.

4. **Temporal lag annotations.** Every edge in the matrix now carries a lag estimate (hours/days/weeks/months/quarters), transforming the static graph into a temporally-aware system. This allows the system to distinguish between chains that execute in hours (carry trade unwind, volatility cascade) and chains that take quarters (monetary policy transmission, fiscal sustainability). Signal attenuates ~30% per hop, making 3-4 hops the effective actionable horizon.

5. **Dominant chain ranking.** Twenty-five transmission chains are ranked by historical explanatory power across four tiers — from primary chains that fire in every cycle (rate transmission, dollar wrecking ball, volatility cascade) to structural chains that operate over quarters (productivity-valuation, CRE-bank solvency). This addresses the "millions of paths" problem by identifying which chains carry the most energy in practice.

The framework is designed to be **complete without being exhaustive.** At 8.8% matrix density, the graph captures all primary transmission mechanisms. The validated expansion path to 15.5% density would capture secondary contagion channels — the cross-asset linkages that dominate in crisis environments. This expansion is documented and ready for implementation.

The principle is not to predict the future. It is to **understand the present quickly enough to respond.** When the next crisis arrives, this framework allows us to trace the causal chain from trigger to consequence in hours, not weeks — and to ask the question that defines macro risk management: *what breaks next?*

---

*End of Report*
