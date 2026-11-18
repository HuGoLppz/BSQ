#include "header.h"

int	print_map(int fd)
{
	char	buf[BUFFER_SIZE];
	int		bytes;

	bytes = read(fd, buf, BUFFER_SIZE);
	while (bytes > 0)
	{
		write(1, buf, bytes);
		bytes = read(fd, buf, BUFFER_SIZE);
	}
	if (bytes < 0)
		return (0);
	return (1);
}
