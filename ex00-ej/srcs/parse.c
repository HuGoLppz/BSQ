/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "bsq.h"

static int	is_printable(char c)
{
	return (c >= 32 && c <= 126);
}

static int	parse_number(char *str, long len, int *result)
{
	long	i;
	int		digit;

	if (len < 1)
		return (0);
	*result = 0;
	i = 0;
	while (i < len)
	{
		if (str[i] < '0' || str[i] > '9')
			return (0);
		digit = str[i] - '0';
		if (*result > (INT_MAX - digit) / 10)
			return (0);
		*result = *result * 10 + digit;
		i++;
	}
	return (*result > 0);
}

static int	check_charset(t_map *map)
{
	if (!is_printable(map->empty) || !is_printable(map->obstacle)
		|| !is_printable(map->full))
		return (0);
	if (map->empty == map->obstacle || map->empty == map->full
		|| map->obstacle == map->full)
		return (0);
	return (1);
}

int	parse_header(t_map *map)
{
	long	i;

	i = 0;
	while (i < map->len && map->buf[i] != '\n')
		i++;
	if (i == map->len || i < 4)
		return (0);
	map->empty = map->buf[i - 3];
	map->obstacle = map->buf[i - 2];
	map->full = map->buf[i - 1];
	if (!check_charset(map))
		return (0);
	if (!parse_number(map->buf, i - 3, &map->rows))
		return (0);
	map->grid = map->buf + i + 1;
	map->grid_len = map->len - i - 1;
	return (1);
}
