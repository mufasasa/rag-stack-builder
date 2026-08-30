# Trajectory: agentic decomposition over the library (Phase 5 verification)

**Date:** 2026-08-30 · **Agent:** Claude Code session connected to the `rag-stack-library` MCP server via the repo's `.mcp.json` (real MCP plumbing, not an in-process shortcut) · **Server config:** hybrid retrieval (post-Iteration-2 default).

**Verification criterion (PLAN.md Phase 5):** a judgment question triggers multiple distinct `search_corpus` calls and a cited answer.

## The judgment question (not in the eval set)

> How did the institution of slavery in Northern Nigeria change under early British administration?

## Agent behavior: decomposition into three focused sub-queries

Per the agent-side instruction shipped in the MCP server's `instructions` string, the question was decomposed and searched separately (three parallel `search_corpus` calls, k=3 each):

1. `slave-raiding by the emirates before British rule`
2. `British proclamation abolition of slavery legal status`
3. `Kano slave market after British occupation slaves liberated`

## What retrieval returned (abridged; scores and full text in the session transcript)

- Sub-query 1 → Shaw Ch. XLIV (Slave-Raiding): raiding "general throughout the Protectorate" between Barth's 1851 visit and British authority; a documented raid yielding 2,000 slaves and 7,000 cattle split among 20,000 raiders; raiding as royal revenue prerogative.
- Sub-query 2 → **Orr Ch. XI (Slavery), pp. 226–227**: the legislative sequence — 1901 Proclamation (legal status of slavery abolished; children born after 31 March 1901 free), 1904 (adds slave-trading as an offence), 1907 (the consolidated law: no property in persons, slave competent to testify, right to assert freedom, transfers prohibited, no compensation to owners); plus Shaw Ch. XLIX on the *doctrine*: abolition of the legal status ≠ abolition of slavery — gradual emancipation "without dislocating the whole machinery of labour," and the frank contemporary argument that sudden abolition would confiscate recognized Mohammedan property and collapse a slave-labour economy.
- Sub-query 3 → Shaw Ch. XLVII: after Kano's capture "the slave-market closed itself" while the rest of the market resumed in three days; **Orr Ch. VI pp. 152–153**: the slave quarter "deserted, the latter having been liberated on the arrival of the British force"; Barth Ch. XXV: the 1851 eyewitness baseline — rows of slaves "arranged in rows like cattle" in Kano's market.

## The cited answer

Under early British administration, slavery in Northern Nigeria was dismantled *legally and gradually* rather than abolished outright:

1. **What existed before:** In 1851 Barth saw slaves sold openly in Kano's market, "arranged in rows like cattle, and staring desperately upon the buyers" (Barth, *Travels*, Ch. XXV). By 1900, slave-raiding "had become general throughout the Protectorate," with emirs' revenues drawn from tribute in slaves and raid tithes (Shaw, *A Tropical Dependency*, Ch. XLIV; Ch. XLIX).
2. **The legal instrument was status-abolition, not slavery-abolition.** The 1901 Proclamation abolished the *legal status* of slavery and freed all children born after 31 March 1901; the 1904 Proclamation added slave-trading as an offence; the 1907 Proclamation consolidated the law — no property in persons, slaves competent to testify and free to assert their freedom, all transfers prohibited, and explicitly no compensation to owners (Orr, *The Making of Northern Nigeria*, Ch. XI, pp. 226–227). Slave-raiding and slave-trading were banned immediately; owning slaves was not, so long as the slave chose to stay (Shaw, Ch. XLIX).
3. **Why gradualism:** contemporaries argued sudden abolition would amount to uncompensated confiscation of property recognized under Islamic law and would dislocate an economy in which "slave power takes the place which steam and electric power take in the West"; the design was for slave-owning to wither economically as raiding stopped and each new generation was born free (Shaw, Ch. XLIX).
4. **Immediate visible effect:** when Kano fell in February 1903, the slave quarter of the market was deserted — the slaves "having been liberated on the arrival of the British force" (Orr, Ch. VI, pp. 152–153) — and "the slave-market closed itself" while ordinary trade resumed within three days (Shaw, Ch. XLVII).

Everything above is drawn from the retrieved passages; the library contains no post-1911 material, so nothing is claimed about how the system evolved after these sources were written.

## Why this trajectory matters

The three sub-queries retrieved *different, complementary* passages (Barth's eyewitness scene, Orr's statute chapter with page cites, Shaw's doctrine chapter) that no single whole-question search surfaced together — the D8 argument ("a judgment question is secretly a bundle of lookup questions") demonstrated live, through the same tool any MCP host gets.
