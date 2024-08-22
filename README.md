# Automated Trading Algorithm for Forex and Crypto

# Overview
This repository hosts a collection of scripts for automated trading based on the identification of H1 order blocks in Forex and cryptocurrency markets. The algorithms are designed to detect key price levels and execute trades based on these patterns, offering a systematic approach to trading.

# Contents
Complete Automated Trader GITHUB.py: The core automated trading algorithm that identifies H1 order blocks on a Forex or cryptocurrency pair. This script supports two-way trading, allowing for both long and short positions based on detected order blocks.

OAT (Orderblock Algorithmic Trader).py: A variant of the Complete Automated Trader with modified strategies for order block identification and trade execution.

stop method calculator.R: A script written in R that simulates the profit and performance of the Complete Automated Trader (GITHUB.py). This helps in evaluating the effectiveness of the trading algorithm under different conditions.

# Features
H1 Order Block Detection: Identifies order blocks on the 1-hour timeframe, widely used by retail traders for decision-making.
Forex and Crypto Support: Compatible with various Forex pairs and cryptocurrency pairs.
Two-Way Trading: Capable of executing trades in both directions, depending on the market conditions.
Performance Simulation: stop method calculator.R provides a simulated analysis of the trading strategy’s profitability.
