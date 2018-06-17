from itertools import islice

FILENAME = 'some_ex.txt'
MIN_SUPPORT = 0.25
NUM_BUSKETS = -1


class Apriori:
    def __init__(self, filename, min_support, num_baskets):
        self.transactions = self.__parse_transactions(filename, num_baskets)
        self.numTransactions = len(self.transactions)
        self.minSupport = min_support
        self.frequentItems = []
        self.results = []
        self.frequentItemsSupport = []

    @staticmethod
    def __parse_transactions(filename, num_baskets):
        """
        Imports transactions from file into dataset.
        Preconditions:
            filename - filename of input transaction file (space delimited)
            numBaskets - Number of baskets to process
        Post-conditions:
            dataset - list of transaction sets
        """
        transactions = []
        if num_baskets == -1:
            with open(filename, 'r') as file:
                for line in file:
                    transactions.append(map(str.strip, line.split()))
        else:
            with open(filename) as file:
                for line in islice(file, num_baskets):
                    transactions.append(map(str.strip, line.split()))
        return list(map(set, transactions))

    def __create_c1(self):
        """
        Creates C1 candidate k-tuples (All items).
        """
        c1 = []
        for transaction in self.transactions:
            for item in transaction:
                if [item] not in c1:
                    c1.append([item])
        c1.sort()
        return list(map(frozenset, c1))

    def __filter_ck(self, ck):
        """
        Filter Ck candidate tuples and return Lk and its supports.
        Preconditions:
            Ck - List of candidate k-tuples
            minSupport - Minumum support threshold
        Post-conditions:
            List of truly frequent k-tuples, k-tuple supports (dict)
        """
        counts = {}
        lk_supports = {}
        lk = []
        for transaction in self.transactions:
            for candidate in ck:
                if candidate.issubset(transaction):
                    if candidate not in counts:
                        counts[candidate] = 1
                    else:
                        counts[candidate] += 1

        for key in counts:
            support = counts[key]/float(self.numTransactions)
            if support >= self.minSupport:
                lk.append(key)
            lk_supports[key] = support
        return lk, lk_supports

    @staticmethod
    def __create_ck(lk, k):
        """
        Creates Ck candidate k-tuples.
        """
        ck = set()
        for a in lk:
            for b in lk:
                union = a | b
                if len(union) == k and a != b:
                    ck.add(union)
        return ck

    def run(self):
        """
        Run Apriori Algorithm
        """
        c1 = self.__create_c1()
        l1, supports = self.__filter_ck(c1)

        self.frequentItems.append(l1)
        self.frequentItemsSupport = supports
        k = 2  # Second pass
        while len(self.frequentItems[k-2]) > 0:
            ck = self.__create_ck(self.frequentItems[k-2], k)
            if ck != set([]):
                lk, support_k = self.__filter_ck(ck)
                self.frequentItemsSupport.update(support_k)
                self.frequentItems.append(lk)
                self.results.append([list(x) for x in lk])
            else:
                break
            k += 1
        return

    def print_results(self):
        """
        Print Frequent Items starting with largest sets first.
        """
        print("Frequent Items:")
        for sets in self.results:
            for item in sets:
                print(item)


if __name__ == '__main__':
    apriori = Apriori(FILENAME, MIN_SUPPORT, NUM_BUSKETS)
    print("Apriori:", FILENAME, "Support:", MIN_SUPPORT, "Baskets:", NUM_BUSKETS)
    apriori.run()
    apriori.print_results()
