# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/11/16 23:45:12 by marvin            #+#    #+#              #
#    Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME		= bsq

CC			= cc
CFLAGS		= -Wall -Wextra -Werror
INCLUDES	= -I includes

HEADER		= includes/bsq.h
SRCS		= srcs/main.c \
			  srcs/read_input.c \
			  srcs/parse.c \
			  srcs/validate.c \
			  srcs/solve.c
OBJS		= $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(NAME)

%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
