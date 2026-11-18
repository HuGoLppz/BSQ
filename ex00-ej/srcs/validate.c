/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   validate.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "bsq.h"

static long	get_line_length(char *str, long len)
{
	long	i;

	i = 0;
	while (i < len && str[i] != '\n')
		i++;
	return (i);
}

static int	is_valid_cell(t_map *map, char c, long col)
{
	if (col == map->cols)
		return (c == '\n');
	return (c == map->empty || c == map->obstacle);
}

int	validate_map(t_map *map)
{
	long	i;
	long	col;

	map->cols = get_line_length(map->grid, map->grid_len);
	if (map->cols == 0)
		return (0);
	if (map->grid_len != (long)map->rows * (map->cols + 1))
		return (0);
	i = 0;
	col = 0;
	while (i < map->grid_len)
	{
		if (!is_valid_cell(map, map->grid[i], col))
			return (0);
		col++;
		if (col > map->cols)
			col = 0;
		i++;
	}
	return (1);
}
