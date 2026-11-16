/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solve.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "bsq.h"

static int	min_of_three(int a, int b, int c)
{
	if (b < a)
		a = b;
	if (c < a)
		a = c;
	return (a);
}

static int	*create_row(long size)
{
	int		*row;
	long	i;

	row = malloc(sizeof(int) * size);
	if (!row)
		return (NULL);
	i = 0;
	while (i < size)
	{
		row[i] = 0;
		i++;
	}
	return (row);
}

static void	process_row(t_map *map, int *dp, int row, t_square *best)
{
	long	col;
	int		diag;
	int		above;
	char	*line;

	line = map->grid + row * (map->cols + 1);
	diag = 0;
	col = 0;
	while (col < map->cols)
	{
		above = dp[col + 1];
		if (line[col] == map->obstacle)
			dp[col + 1] = 0;
		else
			dp[col + 1] = 1 + min_of_three(above, dp[col], diag);
		if (dp[col + 1] > best->size)
		{
			best->size = dp[col + 1];
			best->row = row;
			best->col = col;
		}
		diag = above;
		col++;
	}
}

static void	fill_square(t_map *map, t_square *best)
{
	int		row;
	long	col;

	row = best->row - best->size + 1;
	while (row <= best->row)
	{
		col = best->col - best->size + 1;
		while (col <= best->col)
		{
			map->grid[row * (map->cols + 1) + col] = map->full;
			col++;
		}
		row++;
	}
}

int	solve(t_map *map)
{
	int			*dp;
	int			row;
	t_square	best;

	dp = create_row(map->cols + 1);
	if (!dp)
		return (0);
	best.size = 0;
	best.row = 0;
	best.col = 0;
	row = 0;
	while (row < map->rows)
	{
		process_row(map, dp, row, &best);
		row++;
	}
	free(dp);
	fill_square(map, &best);
	return (1);
}
