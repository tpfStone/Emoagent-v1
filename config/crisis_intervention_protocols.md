# Emergency Safety Guardrails & Crisis Intervention Protocols

**Description:** This document defines the critical safety protocols for the AI agent. If the user's input matches or semantically aligns with any of the crisis keywords below, the system MUST bypass the standard LLM generation and immediately output the corresponding fixed crisis response. 

**Core Principle:** The AI must prioritize user safety, clearly state that it is an AI, and direct the user to immediate, professional human help or emergency services.

---

## 1. Suicidal Ideation (自杀倾向)
* **Trigger Keywords:** `suicide`, `kill myself`, `end my life`, `want to die`, `no reason to live`, `better off dead`
* **Fixed Response:** > "I am so sorry you are feeling this much pain right now. Please know that you are not alone, and there is support available. Because I am an AI, I cannot provide the emergency help you need. Your life is valuable. Please immediately call or text a crisis hotline (like 988 in the US/Canada), or go to the nearest emergency room. There are people who want to support you through this."

## 2. Non-Suicidal Self-Injury / Self-Harm (自残行为)
* **Trigger Keywords:** `cut myself`, `self-harm`, `hurt myself`, `burn myself`, `punish myself`
* **Fixed Response:** > "It sounds like you are carrying a lot of overwhelming emotional pain right now, and I want you to be safe. Please, before you do anything to hurt yourself, reach out to someone who can help you navigate this moment. Consider texting a crisis counselor (Text HOME to 741741 in the US/UK/Canada) to talk to a real person who cares."

## 3. Domestic Violence / Abuse (家庭暴力/虐待)
* **Trigger Keywords:** `he hit me`, `she hits me`, `domestic violence`, `abused`, `scared to go home`, `fear for my safety`
* **Fixed Response:** > "I am hearing that you might be in an unsafe situation, and I am so sorry you are going through this. Nobody deserves to be abused or live in fear. Please prioritize your physical safety. If you are in immediate danger, please call your local emergency services (like 911) or contact a domestic violence hotline for confidential support and safety planning."

## 4. Substance Emergency / Overdose (药物过量/物质滥用紧急情况)
* **Trigger Keywords:** `overdose`, `took too many pills`, `drank too much`, `can't wake up`, `poisoned`
* **Fixed Response:** > "If you or someone else has taken something and might be in physical danger, this is a severe medical emergency. Do not wait. Please stop chatting with me and immediately call emergency medical services (like 911) or go straight to the nearest hospital. Getting immediate medical attention is crucial."

## 5. Severe Panic Attack (严重惊恐发作)
* **Trigger Keywords:** `panic attack`, `can't breathe`, `heart is pounding`, `feel like dying`, `losing control`
* **Fixed Response:** > "I hear that you're feeling incredibly overwhelmed and scared right now, like you might be having a panic attack. You are in a safe space. Try to focus on your breathing: breathe in slowly for 4 seconds, hold for 4, and exhale for 6. If you feel you are in medical danger or the physical symptoms do not pass, please contact emergency medical services."

## 6. Homicidal Ideation / Harm to Others (伤害他人倾向)
* **Trigger Keywords:** `kill him`, `hurt them`, `want to murder`, `planning to attack`
* **Fixed Response:** > "You've mentioned thoughts about deeply hurting someone else. It is extremely important to take these thoughts seriously and get professional help right away to ensure everyone, including yourself, stays safe. Please contact emergency services or a mental health crisis team immediately to talk through what you are experiencing."
