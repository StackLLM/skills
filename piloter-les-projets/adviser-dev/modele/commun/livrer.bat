@echo off
chcp 65001 >nul
title {{NOM}} - Livrer
rem Envoie vers main le dernier commit "livraison" de la recette, seulement si sa CI est verte.
node "%~dp0.github\livrer.mjs"
