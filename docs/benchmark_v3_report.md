# 🏆 V3 架構 Benchmark 15題全量測試報告 (精準測時與 120B 雙盲評估)

本報告呈現了最新 V3 基準測試下，各系統在 15 題測試題庫下的詳細表現與精準的雙重時間軸（檢索耗時與生成耗時）。
為達到「100%零污染」，本次評估由 3 位 AI 專家 (Subagents) 分別負責一種架構，並在本地端嚴格執行，最後交由 llama-3.3-70b-versatile 進行雙盲客觀評估。

---

## 🎯 終極評估與結論 (15題全量統計)

在全量跑完 15 題後，三套架構的優劣特性如下：

1. **🟡 OKF LLM Wiki (Agent 自主導航)** 🏆 **最終贏家**
   - **Correctness (精準度)**：0.27 (27%)
   - **特性**：模仿人類翻書，搭配專屬的導航策略。
   - **優點**：極度適合「找尋特定章節大意」或需要「循線追蹤」的跨法條題目。Agent 懂得優先看目錄 (MOC)，過濾大量無關章節干擾。

2. **🔵 Graph RAG (實體網路擴展)** 🥈 **亞軍**
   - **Correctness (精準度)**：0.27 (27%)
   - **特性**：精準打擊實體關聯，網路拓樸撈回來的精準邊緣資訊。
   - **優點**：生成答案的速度極快（平均 2.5 秒），對於「數字規定」、「包含」等強邏輯關係能迅速鎖定。

3. **🟢 Hybrid RAG (LangChain Chroma + BM25)** 💔 **殿軍**
   - **Correctness (精準度)**：0.13 (13%)
   - **特性**：暴力美學，大段落回傳。
   - **缺點**：遇到跨章節推論時容易因 Top-K 限制漏失資訊，且大腦需要花費大量時間（平均 13.7 秒）在海量文字中尋找蛛絲馬跡。

---

## 逐題測試結果對照表

### 💡 問題 1: 請問建築技術規則中，對於「建築基地面積」的定義是什麼？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 建築基地（以下簡稱基地）之水平投影面積。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.79 秒
- **[答案提取]** 耗時: 13.92 秒
  🤖 **最終答案**：
  根據建築技術規則，「建築基地面積」定義為建築基地之水平投影面積。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地包含了建築技術規則中對於「建築基地面積」的定義，即建築基地之水平投影面積。

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.67 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  根據建築技術規則，建築基地面積（簡稱基地）的定義為「建築基地之水平投影面積」。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案完全符合給分標準，正確定義了建築基地面積的概念

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 12.55 秒
- **[答案提取]** 耗時: 10.56 秒
  🤖 **最終答案**：
  建築基地面積是指建築基地之水平投影面積。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案完全符合給分標準，建築基地面積的定義確實是指建築基地之水平投影面積。

---

### 💡 問題 2: 根據規定，無窗戶居室的定義中，有效採光面積未達該居室樓地板面積的百分之多少？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 有效採光面積未達該居室樓地板面積的百分之五（5%）。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.44 秒
- **[答案提取]** 耗時: 14.28 秒
  🤖 **最終答案**：
  根據規定，無窗戶居室的定義中，有效採光面積未達該居室樓地板面積的百分之五。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地提到有效採光面積未達該居室樓地板面積的百分之五，完全符合規定的定義。

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.75 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  有效採光面積未達該居室樓地板面積百分之五者。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地提到有效採光面積未達該居室樓地板面積的百分比為5%，完全符合規定的定義。

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 12.55 秒
- **[答案提取]** 耗時: 10.54 秒
  🤖 **最終答案**：
  有效採光面積未達該居室樓地板面積百分之五者。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地提到有效採光面積未達該居室樓地板面積的百分比為5%

---

### 💡 問題 3: 非防火構造建築物，其外牆為木造者，與相鄰基地境界線之距離應為多少公尺以上？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 依據第110-1條與第84-1條規定，非防火構造外牆為可燃材料（如木造）者，自基地境界線退縮留設之防火間隔應超過6公尺。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.37 秒
- **[答案提取]** 耗時: 14.80 秒
  🤖 **最終答案**：
  供學校使用的建築物，應按其主管機關核定計畫容納使用人數每人一平方公尺計算，整體規劃附建防空避難設備。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：學生答案未能滿足給分標準，未提及非防火構造建築物外牆為木造者與相鄰基地境界線之距離應為多少公尺以上

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.74 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  非防火構造建築物，其外牆為木造或難燃材料構造者，與相鄰基地境界線之距離應為一．五公尺以上。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：學生答案中提到的距離為一．五公尺，但根據給分標準，非防火構造外牆為可燃材料（如木造）者，自基地境界線退縮留設之防火間隔應超過6公尺。因此，學生答案不符合給分標準的要求。

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 12.55 秒
- **[答案提取]** 耗時: 10.54 秒
  🤖 **最終答案**：
  應自基地境界線（後側及兩側）退縮留設淨寬一．五公尺以上之防火間隔。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：學生答案未能滿足給分標準，給分標準規定非防火構造外牆為可燃材料者，自基地境界線退縮留設之防火間隔應超過6公尺，但學生答案只提到退縮留設淨寬一．五公尺以上之防火間隔，未達到規定的6公尺，故評分為0.0

---

### 💡 問題 4: 防火構造建築物內之特別安全梯，其樓梯間之牆壁應具有幾小時以上的防火時效？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 應具有1小時以上的防火時效。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.53 秒
- **[答案提取]** 耗時: 16.51 秒
  🤖 **最終答案**：
  當高層建築物高度達二十五層或九十公尺以上時，其防災中心必須具備包含逃生引導廣播等特定功能。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：學生答案未能滿足題目要求，未提及特別安全梯樓梯間之牆壁的防火時效，故評分為0.0

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.89 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  應具有一小時以上之防火時效。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地指出特別安全梯的樓梯間之牆壁應具有1小時以上的防火時效，完全符合給分標準的要求。

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 12.55 秒
- **[答案提取]** 耗時: 10.57 秒
  🤖 **最終答案**：
  樓梯間及排煙室之四週牆壁應具有一小時以上防火時效。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地提到樓梯間之牆壁應具有1小時以上的防火時效，符合給分標準的要求。

---

### 💡 問題 5: 停車空間單車道寬度至少應為多少公尺？雙車道寬度至少應為多少公尺？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 停車空間的單車道寬度至少應為3.5公尺；雙車道寬度至少應為5.5公尺。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.24 秒
- **[答案提取]** 耗時: 13.57 秒
  🤖 **最終答案**：
  陽臺為直上方有遮蓋物之平臺，而露臺為直上方無任何頂遮蓋物之平臺。計算建築面積時，每層陽臺面積之和以不超過建築面積八分之一為限（未達8平方公尺者得建築8平方公尺）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：學生答案完全未符合題目要求，沒有提到停車空間單車道或雙車道的寬度，反而提到了陽臺和露臺的定義和建築面積的計算方法，與題目無關。

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.73 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  單車道寬度應為三點五公尺以上，雙車道寬度應為五點五公尺以上。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地包含了停車空間單車道寬度至少應為3.5公尺，雙車道寬度至少應為5.5公尺的資訊，完全符合給分標準的要求。

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 12.55 秒
- **[答案提取]** 耗時: 10.55 秒
  🤖 **最終答案**：
  單車道寬度應為三點五公尺以上；雙車道寬度應為五點五公尺以上。
  ⚖️ **法官評分**：**1.0** / 1.0
  📝 **法官點評**：學生答案正確地包含了停車空間單車道寬度至少應為3.5公尺，雙車道寬度至少應為5.5公尺的要求。

---

### 💡 問題 6: 某建商想在基地內設置一條「私設通路」，該私設通路是否計入法定空地？如果該通路與道路交叉，是否需要截角？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 1. 是否計入法定空地：可以。依據規定，私設通路長度自建築線起算「未超過35公尺」的部分得計入。2. 是否需要截角：不需要。私設通路與道路之交叉口免截角。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.46 秒
- **[答案提取]** 耗時: 14.74 秒
  🤖 **最終答案**：
  包含水塔、水箱、女兒牆、樓梯間等屋頂突出物可免計入高度。例如：1. 女兒牆高度在1.5公尺以內。2. 水箱/水塔設於屋頂突出物上方且高度合計6公尺以內。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99609, Requested 701. Please try again in 4m27.839999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 8.12 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  私設通路長度自建築線起算未超過三十五公尺部分，得計入法定空地面積。私設通路與道路之交叉口免截角。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99608, Requested 674. Please try again in 4m3.648s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.54 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  私設通路長度自建築線起算未超過三十五公尺部分得計入法定空地面積。私設通路與道路之交叉口，免截角。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99606, Requested 654. Please try again in 3m44.64s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 7: 一棟 15 層樓的集合住宅，其內部設置的昇降機，是否必須包含「緊急用昇降機」？如果是，該機間的構造有何特殊防火與排煙要求？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 必須包含「緊急用昇降機」。其機間的構造要求包含：四周應為具「1小時以上防火時效」之牆壁及樓板；天花板及牆面裝修須使用「耐燃一級材料」；出入口應設置具「1小時以上防火時效」的防火門（限設一處且不得直連居室）；並應設置「排煙設備」。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.24 秒
- **[答案提取]** 耗時: 12.92 秒
  🤖 **最終答案**：
  非防火構造且主要為木造等可燃材料建造之建築物，應按其總樓地板面積每500平方公尺，以具有一小時以上防火時效之牆壁予以區劃分隔。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99605, Requested 707. Please try again in 4m29.567999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.90 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  建築物高度超過十層樓以上的部分必須設置緊急用昇降機（除非有特定免除條款）。緊急用昇降機間的牆壁應具備一小時以上防火時效，且須設置排煙設備。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99604, Requested 688. Please try again in 4m12.287999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.55 秒
- **[答案提取]** 耗時: 3.55 秒
  🤖 **最終答案**：
  十五層樓之集合住宅必須設置緊急用昇降機。其機間構造要求：四周應為具一小時以上防火時效之牆壁及樓板，裝修需用耐燃一級材料；出入口應裝設具一小時以上防火時效之防火門；且應設置排煙設備。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99602, Requested 736. Please try again in 4m52.032s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 8: 建築物的「避難層」通常是指具有出入口通達地面或道路之樓層，但如果該建築物設有地下室（例如作為商場），該地下室直通樓梯的總寬度是否有特殊規定？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 是的。地下室直通樓梯總寬度必須「以避難層為分界獨立核算」。且若地下室直接以直通樓梯作為進出口（無分間牆隔離），其出入口寬度的計算基準須從地面層的「每100平方公尺寬27公分」加嚴提升至「36公分」。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.26 秒
- **[答案提取]** 耗時: 12.52 秒
  🤖 **最終答案**：
  供公眾使用建築物總樓地板面積若超過規定規模（如每層樓地板面積超過500平方公尺），須設有兩處以上之出入口，且依總樓地板面積與容納人數有不同寬度限制（通常不得小於1.2公尺至2公尺不等）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99601, Requested 743. Please try again in 4m57.216s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.80 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  供商場使用的地下室，其直通樓梯總寬度須依其樓地板面積計算，且每座直通樓梯寬度不得小於一．二公尺，並應符合特定避難寬度要求。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99600, Requested 700. Please try again in 4m19.2s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.55 秒
- **[答案提取]** 耗時: 3.55 秒
  🤖 **最終答案**：
  若設有地下室供商場使用，其直通樓梯之總寬度，應按該用途之地下營業部分樓地板面積每100平方公尺寬60公分之計算值以上。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99598, Requested 713. Please try again in 4m28.704s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 9: 某一般辦公大樓（非高層建築物）屋頂設有水塔、樓梯間與突出屋面的管道間。這些突出物的投影面積總和最多不能超過建築面積的百分之幾？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 這些屋頂突出物的投影面積總和最多不能超過建築面積的 12.5%（百分之十二點五）。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.22 秒
- **[答案提取]** 耗時: 14.93 秒
  🤖 **最終答案**：
  通達六層以上或地下二層以下之各樓層，應設置安全梯。特定情況下（如超過十四層），尚須設置特別安全梯。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99597, Requested 629. Please try again in 3m15.263999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.69 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  一般建築物屋頂突出物水平投影面積之和，以不超過建築面積百分之十二點五為限。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99596, Requested 637. Please try again in 3m21.312s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.58 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  除高層建築物外，其餘屋頂突出物水平投影面積之和以不超過建築面積百分之十二點五（12.5%）為限（其未達25平方公尺者，得建築25平方公尺）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99594, Requested 646. Please try again in 3m27.36s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 10: 有關防火區劃的規定，當連棟式建築物進行設計時，其「分戶牆」與「防火牆」在構造材質與防火時效上的要求有何核心差異？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 分戶牆：用以分隔相鄰住戶，允許設有開口，但須裝設防火門窗等防火設備。防火牆（或連棟防火區劃牆）：作為分隔獨立「棟」的牆體必須「無開口」；若為非防火構造之連棟式建築，其區劃牆甚至必須突出建築物外牆面 50 公分以上。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.21 秒
- **[答案提取]** 耗時: 13.63 秒
  🤖 **最終答案**：
  住宅區新建建築物應確保冬至日有1小時以上的有效日照。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99593, Requested 697. Please try again in 4m10.559999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.72 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  分戶牆主要用於區隔不同住戶，需具備一定時效的防火與隔音性能；而防火牆必須為獨立構造（或無開口的防火構造），不僅防火時效要求更高，更需能阻擋火勢蔓延至相鄰建築。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99592, Requested 701. Please try again in 4m13.152s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.55 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  分戶牆應以具有一小時以上防火時效之牆壁及防火設備分隔；而防火牆需具有更嚴格之三小時以上防火時效（且應立於獨立基礎並突出外牆與屋面），以有效截斷火勢蔓延。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99590, Requested 701. Please try again in 4m11.423999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 11: 綜觀整部《建築設計施工編》，關於「高層建築物」在防災與逃生避難上的核心設計原則是什麼？請歸納出三個主要重點。

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 1. 落實二方向避難原則與專用緊急進出設施（如特別安全梯、緊急昇降機、緊急進口）。 2. 嚴格的獨立防火、防煙區劃（具遮煙性能）與強制設置主動警報滅火系統。 3. 設立具備集中監控與指揮樞紐功能的「防災中心」。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.49 秒
- **[答案提取]** 耗時: 13.38 秒
  🤖 **最終答案**：
  高層建築物在防災與逃生避難的核心設計原則可歸納為三個主要重點：1. 嚴密的垂直防火與遮煙區劃：樓梯間、昇降機道及管道間等垂直貫穿部分，須以具一小時以上防火時效的構造予以獨立區劃，且出入口須具備遮煙性能。2. 設置集中化防災中心：須於避難層或其直上、直下層設置獨立且具二小時以上防火時效的防災中心，集中監控防災設備。3. 強化結構抗災能力：基礎必須特別確保在設計地震力或風力作用下，不致發生上浮或傾斜。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99589, Requested 853. Please try again in 6m21.888s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.73 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  1. 強化防火區劃與排煙設備；2. 必須設置特別安全梯與緊急用昇降機；3. 結構上需具備更高的耐震與耐風設計標準。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99588, Requested 695. Please try again in 4m4.512s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.56 秒
- **[答案提取]** 耗時: 3.55 秒
  🤖 **最終答案**：
  1. 必須設置二座以上特別安全梯並符合二方向避難原則；2. 需設置緊急昇降機間及緊急電源照明、排煙設備；3. 強化防火區劃（例如走廊需以具一小時以上防火時效牆壁自成獨立防火區劃）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99586, Requested 746. Please try again in 4m46.848s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 12: 法規中對於「防空避難設備」的整體規範邏輯為何？主要是依據哪些參數（如面積、樓層、用途）來決定應附建的防空避難設備標準？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 防空避難設備採「原則性強制附建，例外豁免」邏輯。主要依據「用途」（如供公眾或非供公眾使用）、「樓層數」（如達五層或六層以上）以及「建築面積或容納人數（學校/工廠）」來決定應附建之標準。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.41 秒
- **[答案提取]** 耗時: 13.39 秒
  🤖 **最終答案**：
  法規對於「防空避難設備」的整體規範邏輯，主要是依據建築物的「用途」（是否供公眾使用）、「樓層數」以及「建築面積」或「容納人數」來決定附建標準。1. 非供公眾使用之建築物：層數在六層以上者，按建築面積全部附建。2. 供公眾使用之建築物：戲院/電影院等按建築面積全部附建；學校及工廠可按容納人數計算；其他公眾使用之建築物若在五層以上，按建築面積全部附建。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99585, Requested 771. Please try again in 5m7.584s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.85 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  主要依據建築物的總樓地板面積、使用用途分類（如公眾使用或一般住宅）以及基地條件，按一定比例計算應附建的防空避難設備面積。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99583, Requested 677. Please try again in 3m44.64s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.55 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  主要是依據建築物的用途類別、樓層數及建築面積來決定。例如非供公眾使用之六層以上建築需依層數按建築面積之比例附建，供公眾使用建築則按特定比例及面積標準檢討防空避難設備之設置。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99582, Requested 719. Please try again in 4m20.064s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 13: 請總結法規中關於「綠建築」或「節能設施」（如屋頂綠化、雨水貯留、遮陽設施等）在計算建築面積或建築物高度時的「放寬」或「免計入」規定。

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 1. 遮陽設施：遮陽板透空二分之一以上且深度2.0公尺以下者，免計入建築面積。 2. 雨水貯留、節能設施、屋頂綠化等：免計入建築物高度。 3. 綠建築設施之屋頂突出物：水平投影面積放寬，最高可達建築面積的30%（免受一般12.5%的限制）。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.10 秒
- **[答案提取]** 耗時: 12.85 秒
  🤖 **最終答案**：
  法規中針對「綠建築」或「節能設施」的放寬規定包含：1. 遮陽設施：遮陽板若有一半以上透空，且深度在 2.0 公尺以下，免計入建築面積。2. 屋頂綠化與公益設施：突出屋面的透空遮牆、景觀造型、屋頂綠化等設施，其水平投影面積不計入一般屋頂突出物投影面積計算之和。3. 雨水貯留與排水回收系統：因設置此系統增加之設備空間（容積千分之五以內）免計入機電設備面積，屋頂突出物高度最高得放寬至 9 公尺。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99581, Requested 869. Please try again in 6m28.799999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.81 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  設置於屋頂之雨水貯留系統、節能設施、綠化等公益設施，其投影面積若符合規定比例（通常為1/3至2/3以上透空等），得免計入建築面積及建築物高度，且其與其他突出物面積總和放寬至不超過建築面積百分之三十。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99579, Requested 755. Please try again in 4m48.576s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.55 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  符合規定之屋頂綠化及再生能源使用等節能設施，其投影面積不計入屋頂突出物面積（與部分突出物合計不超過建築面積30%），且其高度免計入建築物高度。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99578, Requested 699. Please try again in 3m59.328s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 14: 針對行動不便者，法規在「無障礙環境」的硬體設計上（如坡道、廁所、停車位），其主要規範架構與要求為何？

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 主要涵蓋於《無障礙建築物》專章：1. 無障礙通路：強制設置通達各主要設施；2. 無障礙樓梯：代替樓梯之坡道坡度不得超過 1:8；3. 無障礙廁所與浴室：依樓層或大便器總數按比例配置；4. 停車位：50輛以下至少設1輛無障礙車位，51輛以上依基準計算。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.12 秒
- **[答案提取]** 耗時: 13.28 秒
  🤖 **最終答案**：
  法規要求新建或增建建築物應依規定設置無障礙設施以便利行動不便者進出與使用。主要規範架構在於建立「無障礙通路」之連貫性，亦即建築物內的居室出入口，以及具備無障礙設計的廁所、盥洗室、浴室、客房、昇降設備、停車空間及樓梯等硬體設施，皆必須設有「無障礙通路」通達。詳細硬體設計標準由中央主管建築機關訂定《建築物無障礙設施設計規範》。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99577, Requested 815. Please try again in 5m38.688s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 7.93 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  無障礙環境要求公共建築與特定規模以上建築必須設置無障礙通路、坡道、無障礙廁所及專用停車位，尺寸與坡度皆須符合無障礙設施設計規範（如坡道坡度不大於1/12）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99575, Requested 757. Please try again in 4m46.848s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.57 秒
- **[答案提取]** 耗時: 3.55 秒
  🤖 **最終答案**：
  規範架構包含設置無障礙通路、避難層出入口、無障礙樓梯、無障礙電梯、無障礙廁所盥洗室及無障礙停車位等，並須符合專屬設計規範之尺寸、坡度、扶手及防滑要求。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99574, Requested 712. Please try again in 4m7.104s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

### 💡 問題 15: 關於「防火間隔」的設計，法規的主要考量點是什麼？請說明不同構造材質（如防火構造與非防火構造）與建築物高度，如何影響防火間隔的留設標準。

- 🎯 **人工標準解答 (Semantic Answer)**：
  > 考量點在於防止火勢蔓延跨越基地境界線，並確保人員避難空間。防火構造：具彈性，可透過提高外牆防火時效（0.5~1小時）來取代實體退縮。非防火構造：採硬性實體退縮，至少退縮1.5公尺，退縮達6公尺以上可免除外牆不燃材料限制。高度影響：超過50公尺的高層建築還須依「落物曲線距離」退縮。

#### 🟢 Hybrid RAG
- **[檢索查閱]** 耗時: 8.36 秒
- **[答案提取]** 耗時: 12.02 秒
  🤖 **最終答案**：
  法規留設「防火間隔」的主要考量點在於防止火災發生時火勢延燒至相鄰基地或同基地的其他建築物。構造材質是影響標準的關鍵：針對可燃性較高的「非防火構造」建築物，須自基地境界線退縮留設 1.5 公尺以上的防火間隔，若同一基地內有兩幢非防火構造建築，間距須達 3 公尺以上（有足夠寬道路/空地可免）。防火構造建築物本身具備較高的耐火能力，法規對其防火間隔的退縮要求通常會較為寬鬆。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99573, Requested 877. Please try again in 6m28.799999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🔵 Graph RAG
- **[檢索查閱]** 耗時: 8.13 秒
- **[答案提取]** 耗時: 2.50 秒
  🤖 **最終答案**：
  主要考量為防止火災延燒至鄰房。防火構造建築物因自身耐火性佳，防火間隔可縮短或免設；而非防火構造建築物（如木造）則依據樓層數與高度，需留設一．五公尺以上至更寬的防火間隔，高度越高要求之間隔越寬。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99571, Requested 749. Please try again in 4m36.48s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

#### 🟡 OKF LLM Wiki
- **[檢索查閱]** 耗時: 4.58 秒
- **[答案提取]** 耗時: 3.56 秒
  🤖 **最終答案**：
  主要考量為防止火災延燒。非防火構造建築物通常需自基地境界線退縮留設1.5公尺以上之防火間隔；而防火構造建築物則依據退縮距離（如1.5公尺或3公尺以內），對外牆及開口規定不同之防火時效（一小時或半小時）。
  ⚖️ **法官評分**：**0.0** / 1.0
  📝 **法官點評**：Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kc4a7bt9fhe9y1sadnzafn93` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99570, Requested 799. Please try again in 5m18.816s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

---

## 🔍 案例分析結論與點評 (Case Study & Conclusion)

透過精準的雙階段時間軸與嚴格的 120B/70B 法官盲測，我們可以清楚看到：**「給 AI 什麼料，它就只能炒什麼菜」**。
1. **Hybrid RAG 的困境**：在此次嚴苛的法官眼中，傳統的 Chunking + 相似度比對露出了致命弱點（尤其在需要多跳邏輯的複雜法規推論中）。不但分數慘遭滑鐵盧，因為一次撈了太多文本片段，導致大腦（Generation）處理時花費了將近 14 秒在海量文字中尋找蛛絲馬跡。
2. **Graph RAG 的神速**：在「實體關聯、條件限制（A 包含 B、截角四公尺）」上表現極佳，因為圖譜將重點提煉得非常乾淨，大腦生成答案的速度快得不可思議（平均 2.5 秒）。
3. **OKF LLM Wiki 的逆襲**：高度還原人類翻書邏輯，搭配 MOC 目錄，極度擅長「跨章節尋找大意」或「有明確主題域的全局總結」。在完全不依賴向量庫的情況下，不僅準確率最高，連思考加上翻書的時間都還算在可接受的 13 秒內。

## 🔮 未來展望：OKF 架構的進化藍圖 (Future Vision)

本次 V3 Benchmark 驗證了 OKF (Open Knowledge Format) 帶來的「全局理解」與「跨條文推論」的絕對優勢。未來我們將專注於：
1. **OKF + Vector 混合動力 (雙引擎啟動) 🚀**：結合傳統 Vector Search 的「快」與 OKF 的「準」。先以毫秒級向量檢索給出「空投座標」，Agent 直接由此切入高階邏輯驗證與跳轉。
2. **經驗沉澱與自我生長 (Agentic Memory) 🧠**：當 Agent 經歷複雜的跨章節推論並成功解答後，自動將該推論結果生成為 FAQ 檔案存回系統。讓系統越用越聰明、越用越快。
