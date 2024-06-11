start.time <- Sys.time()
x <- read.csv("C:/Users/Grego/Downloads/EURUSD_M1.csv")

ratio <- c(5)
entry_depth <- c(0)
stop_depth <- c(0.5)
trigger_depth <- c(0)
initial_account_size <- 1
risk_per_trade <- 0.01
account_size <- array(initial_account_size, dim = c(nrow(x), length(ratio), length(entry_depth), length(stop_depth), length(trigger_depth)))
entry_array <- array(NA, dim = c(length(ratio), length(entry_depth), length(stop_depth), length(trigger_depth), 5, nrow(x)))
k_array <- array(1, dim = c(length(ratio), length(entry_depth), length(stop_depth), length(trigger_depth)))
hours <- matrix(nrow = 0, ncol = 7)
orderblocks <- matrix(nrow = 0, ncol = 2)
ii <- 1
spread <- 0.00005

while (ii < nrow(x)){
  start <- ii
  open <- x[start, "Open"]
  while ((substr(x[ii, "Time"], 12, 13) == substr(x[ii + 1, "Time"], 12, 13)) & (ii + 1 < nrow(x))){
    ii <- ii + 1
  }
  end <- ii
  close <- x[end, "Close"]
  high <- max(x[start:end, "High"])
  low <- min(x[start:end, "Low"])
  hours <- rbind(hours, c(open, high, low, close, start, end, end - start + 1))
  ii <- end + 1
}
plot(hours[, 3], type = "l")

for (i in 1:nrow(hours)){
  if (i + 2 <= nrow(hours)){
    if (hours[i, 1] > hours[i, 4]){#if it is a down candle
      first_close_above <- 1
      next_down_candle <- 1
      
      while ((hours[i + first_close_above, 4] < hours[i, 2]) & (i + first_close_above < nrow(hours))){
        first_close_above <- first_close_above + 1
      }
      while ((hours[i + next_down_candle, 1] < hours[i + next_down_candle, 4]) & (i + next_down_candle < nrow(hours)) & (next_down_candle <= first_close_above)){#finds next down candle
        next_down_candle <- next_down_candle + 1
      }
      if (first_close_above <= next_down_candle){# ORDER BLOCK FORMED
        orderblocks <- rbind(orderblocks, c(i, i + first_close_above))
        minimum <- min(hours[i:(i + first_close_above), 3])
        block_size <- hours[i, 2] - minimum
        
        for (e in 1:length(entry_depth)){
          entry_price <- hours[i, 2] - block_size * entry_depth[e]
          for (t in 1:length(trigger_depth)){
            trigger_index <- 1
            trigger_price <- entry_price - block_size * trigger_depth[t]
            while ((x[hours[i + first_close_above, 6] + trigger_index, "Low"] > trigger_price) & (hours[i + first_close_above, 6] + trigger_index + 1 < nrow(x))){
              trigger_index <- trigger_index + 1
            }
            if (x[hours[i + first_close_above, 6] + trigger_index, "Low"] <= trigger_price){# PENDING BUY STOP PLACED
              entry_index <- 0
              while ((x[hours[i + first_close_above, 6] + trigger_index + entry_index, "High"] < entry_price) & (hours[i + first_close_above, 6] + trigger_index + entry_index + 1 < nrow(x))){
                entry_index <- entry_index + 1
              }
              if (x[hours[i + first_close_above, 6] + trigger_index + entry_index, "High"] >= entry_price){# TRADE ENTERED
                for (s in 1:length(stop_depth)){
                  sl_index <- 0
                  sl_price <- entry_price - block_size * stop_depth[s] + spread/2
                  while((x[hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index, "Low"] > sl_price) & (hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index < nrow(x))){
                    sl_index <- sl_index + 1
                  }
                  for (r in 1:length(ratio)){
                    k <- 1
                    tp_index <- 1
                    tp_price <- entry_price + ratio[r] * block_size * stop_depth[s] + spread/2
                    while ((x[hours[i + first_close_above, 6] + trigger_index + entry_index + tp_index, "High"] < tp_price) & (hours[i + first_close_above, 6] + trigger_index + entry_index + tp_index < nrow(x)) & (tp_index <= sl_index)){
                      tp_index <- tp_index + 1
                    }
                    if (tp_index < sl_index){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_above, 6] + trigger_index + entry_index, hours[i + first_close_above, 6] + trigger_index + entry_index + tp_index, ratio[r], i, i + first_close_above)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (sl_index < tp_index){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_above, 6] + trigger_index + entry_index, hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_above)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index < nrow(x)){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_above, 6] + trigger_index + entry_index, hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_above)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (x[hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index, "Low"] <= sl_price){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_above, 6] + trigger_index + entry_index, hours[i + first_close_above, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_above)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (x[hours[i + first_close_above, 6] + trigger_index + entry_index + tp_index, "High"] >= tp_price){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_above, 6] + trigger_index + entry_index, hours[i + first_close_above, 6] + trigger_index + entry_index + tp_index, ratio[r], i, i + first_close_above)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    }
                  }
                }
              }
            }
          }
        }
      }
    } else if (hours[i, 1] < hours[i, 4]){#if it is an up candle
      first_close_below <- 1
      next_up_candle <- 1
      
      while ((hours[i + first_close_below, 4] > hours[i, 3]) & (i + first_close_below < nrow(hours))){
        first_close_below <- first_close_below + 1
      }
      while ((hours[i + next_up_candle, 1] > hours[i + next_up_candle, 4]) & (i + next_up_candle < nrow(hours)) & (next_up_candle <= first_close_below)){#finds next up candle
        next_up_candle <- next_up_candle + 1
      }
      if (first_close_below <= next_up_candle){# ORDER BLOCK FORMED
        orderblocks <- rbind(orderblocks, c(i, i + first_close_below))
        maximum <- max(hours[i:(i + first_close_below), 2])
        block_size <- maximum - hours[i, 3]
        
        for (e in 1:length(entry_depth)){
          entry_price <- hours[i, 3] + block_size * entry_depth[e]
          for (t in 1:length(trigger_depth)){
            trigger_index <- 1
            trigger_price <- entry_price + block_size * trigger_depth[t]
            while ((x[hours[i + first_close_below, 6] + trigger_index, "High"] < trigger_price) & (hours[i + first_close_below, 6] + trigger_index + 1 < nrow(x))){
              trigger_index <- trigger_index + 1
            }
            if (x[hours[i + first_close_below, 6] + trigger_index, "High"] >= trigger_price){
              entry_index <- 0
              while ((x[hours[i + first_close_below, 6] + trigger_index + entry_index, "Low"] > entry_price) & (hours[i + first_close_below, 6] + trigger_index + entry_index + 1 < nrow(x))){
                entry_index <- entry_index + 1
              }
              if (x[hours[i + first_close_below, 6] + trigger_index + entry_index, "Low"] <= entry_price){
                for (s in 1:length(stop_depth)){
                  sl_index <- 0
                  sl_price <- entry_price + block_size * stop_depth[s] - spread/2
                  while((x[hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index, "High"] < sl_price) & (hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index < nrow(x))){
                    sl_index <- sl_index + 1
                  }
                  for (r in 1:length(ratio)){
                    k <- 1
                    tp_index <- 1
                    tp_price <- entry_price - ratio[r] * block_size * stop_depth[s] - spread/2
                    while ((x[hours[i + first_close_below, 6] + trigger_index + entry_index + tp_index, "Low"] > tp_price) & (hours[i + first_close_below, 6] + trigger_index + entry_index + tp_index < nrow(x)) & (tp_index <= sl_index)){
                      tp_index <- tp_index + 1
                    }
                    if (tp_index < sl_index){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_below, 6] + trigger_index + entry_index, hours[i + first_close_below, 6] + trigger_index + entry_index + tp_index, ratio[r], i, i + first_close_below)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (sl_index < tp_index){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_below, 6] + trigger_index + entry_index, hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_below)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index < nrow(x)){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_below, 6] + trigger_index + entry_index, hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_below)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (x[hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index, "High"] >= sl_price){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_below, 6] + trigger_index + entry_index, hours[i + first_close_below, 6] + trigger_index + entry_index + sl_index, -1, i, i + first_close_below)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    } else if (x[hours[i + first_close_below, 6] + trigger_index + entry_index + tp_index, "Low"] <= tp_price){
                      entry_array[r, e, s, t, , k_array[r, e, s, t]] <- c(hours[i + first_close_below, 6] + trigger_index + entry_index, hours[i + first_close_below, 6] + trigger_index + entry_index + tp_index, ratio[r], i, i + first_close_below)
                      k_array[r, e, s, t] <- k_array[r, e, s, t] + 1
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
for (e in 1:length(entry_depth)){#fills up the account_size matrix
  for (s in 1:length(stop_depth)){
    for (r in 1:length(ratio)){
      for (t in 1:length(trigger_depth)){
        temp_matrix <- matrix(nrow = 0, ncol = 5)
        q <- 1
        while (is.na(entry_array[r, e, s, t, 1, q]) == FALSE){
          temp_matrix <- rbind(temp_matrix, c(entry_array[r, e, s, t, , q]))
          q <- q + 1
        }
        temp_matrix <- temp_matrix[order(temp_matrix[,1], decreasing = FALSE),]
        for (x in 1:nrow(temp_matrix)){
          for (y in temp_matrix[x, 2]:nrow(account_size)){
            account_size[y, r, e, s, t] <- account_size[y, r, e, s, t] + risk_per_trade * temp_matrix[x, 3] * account_size[temp_matrix[x,1], r, e, s, t]
          }
        }
      }
    }
  }
}
pdf(file = paste("EURUSD stop method combos", spread))
for (r in 1:length(ratio)){
  for (e in 1:length(entry_depth)){
    for (s in 1:length(stop_depth)){
      for (t in 1:length(trigger_depth)){
        plot(account_size[, r, e, s, t], main = paste(ratio[r], entry_depth[e], stop_depth[s], trigger_depth[t]), type = "l")
        mtext(paste("min =",round(min(account_size[, r, e, s, t]), 4), " max =", round(max(account_size[, r, e, s, t]), 4)), side = 3)
      }
    }
  }
}
dev.off()

candidates <- matrix(nrow = 0,ncol = 5)

pdf(file = paste("EURUSD candidates", spread))
for (r in 1:length(ratio)){
  for (e in 1:length(entry_depth)){
    for (s in 1:length(stop_depth)){
      for (t in 1:length(trigger_depth)){
        if (account_size[nrow(account_size), r, e, s, t] >= 1){
          candidates <- rbind(candidates, c(ratio[r], entry_depth[e], stop_depth[s], trigger_depth[t], account_size[nrow(account_size), r, e, s, t]))
          plot(account_size[, r, e, s, t], main = paste(ratio[r], entry_depth[e], stop_depth[s], trigger_depth[t]), type = "l")
        }
      }
    }
  }
}
dev.off()
candidates
end.time <- Sys.time()
total.time <- round(end.time - start.time, 2)
total.time
