/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   read_input.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "bsq.h"

static int	grow_buffer(t_map *map, long *capacity)
{
	char	*new_buf;
	long	i;

	new_buf = malloc(*capacity * 2);
	if (!new_buf)
	{
		free(map->buf);
		return (0);
	}
	i = 0;
	while (i < map->len)
	{
		new_buf[i] = map->buf[i];
		i++;
	}
	free(map->buf);
	map->buf = new_buf;
	*capacity *= 2;
	return (1);
}

int	read_all(int fd, t_map *map)
{
	long	capacity;
	long	bytes;

	capacity = BUFFER_SIZE;
	map->len = 0;
	map->buf = malloc(capacity);
	if (!map->buf)
		return (0);
	bytes = read(fd, map->buf, capacity);
	while (bytes > 0)
	{
		map->len += bytes;
		if (map->len == capacity && !grow_buffer(map, &capacity))
			return (0);
		bytes = read(fd, map->buf + map->len, capacity - map->len);
	}
	if (bytes < 0)
	{
		free(map->buf);
		return (0);
	}
	return (1);
}
