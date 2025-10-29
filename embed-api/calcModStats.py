from abc import ABC, abstractmethod


# Utility/stat functions as per osu-web.js logic
def hr_stat(n):
    return min(n * 1.4, 10)


def ez_stat(n):
    return n / 2


def dt_bpm(n):
    return n * 1.5


def dt_length(n):
    return n / 1.5


def dt_od(n):
    return (53 + 8 * n) / 12


def dt_ar(n):
    if n <= 5:
        return min((75 + 8 * n) / 15, 11)
    else:
        return min((13 + 2 * n) / 3, 11)


def ht_bpm(n):
    return n * 0.75


def ht_length(n):
    return n * 0.75


def ht_od(n):
    return (-53 + 16 * n) / 12


def ht_ar(n):
    if n <= 5:
        return (4 / 3) * n - 5
    elif n > 7:
        return (4 / 3) * n - 13 / 3
    else:
        return (4 / 3) * n - 19 / 3


class ModStatCalculator(ABC):
    def __init__(self, ar, od, cs, hp, bpm, length):
        self.ar = ar
        self.od = od
        self.cs = cs
        self.hp = hp
        self.bpm = bpm
        self.length = length

    @abstractmethod
    def calculate_ar(self):
        pass

    @abstractmethod
    def calculate_od(self):
        pass

    @abstractmethod
    def calculate_cs(self):
        pass

    @abstractmethod
    def calculate_hp(self):
        pass

    @abstractmethod
    def calculate_bpm(self):
        pass

    @abstractmethod
    def calculate_length(self):
        pass

    def calculate_all(self):
        return dict(
            ar=self.calculate_ar(),
            od=self.calculate_od(),
            cs=self.calculate_cs(),
            hp=self.calculate_hp(),
            bpm=self.calculate_bpm(),
            length=self.calculate_length(),
        )


class NoMod(ModStatCalculator):
    def calculate_ar(self):
        return self.ar

    def calculate_od(self):
        return self.od

    def calculate_cs(self):
        return self.cs

    def calculate_hp(self):
        return self.hp

    def calculate_bpm(self):
        return self.bpm

    def calculate_length(self):
        return self.length


class HardRock(ModStatCalculator):
    def __init__(self, base):
        super().__init__(base.ar, base.od, base.cs, base.hp, base.bpm, base.length)
        self.base = base

    def calculate_ar(self):
        return hr_stat(self.base.calculate_ar())

    def calculate_od(self):
        return hr_stat(self.base.calculate_od())

    def calculate_cs(self):
        return self.base.calculate_cs() * 1.3

    def calculate_hp(self):
        return hr_stat(self.base.calculate_hp())

    def calculate_bpm(self):
        return self.base.calculate_bpm()

    def calculate_length(self):
        return self.base.calculate_length()


class Easy(ModStatCalculator):
    def __init__(self, base):
        super().__init__(base.ar, base.od, base.cs, base.hp, base.bpm, base.length)
        self.base = base

    def calculate_ar(self):
        return ez_stat(self.base.calculate_ar())

    def calculate_od(self):
        return ez_stat(self.base.calculate_od())

    def calculate_cs(self):
        return ez_stat(self.base.calculate_cs())

    def calculate_hp(self):
        return ez_stat(self.base.calculate_hp())

    def calculate_bpm(self):
        return self.base.calculate_bpm()

    def calculate_length(self):
        return self.base.calculate_length()


class DoubleTime(ModStatCalculator):
    def __init__(self, base):
        super().__init__(base.ar, base.od, base.cs, base.hp, base.bpm, base.length)
        self.base = base

    def calculate_ar(self):
        return dt_ar(self.base.calculate_ar())

    def calculate_od(self):
        return dt_od(self.base.calculate_od())

    def calculate_cs(self):
        return self.base.calculate_cs()

    def calculate_hp(self):
        return self.base.calculate_hp()

    def calculate_bpm(self):
        return dt_bpm(self.base.calculate_bpm())

    def calculate_length(self):
        return dt_length(self.base.calculate_length())


class HalfTime(ModStatCalculator):
    def __init__(self, base):
        super().__init__(base.ar, base.od, base.cs, base.hp, base.bpm, base.length)
        self.base = base

    def calculate_ar(self):
        return ht_ar(self.base.calculate_ar())

    def calculate_od(self):
        return ht_od(self.base.calculate_od())

    def calculate_cs(self):
        return self.base.calculate_cs()

    def calculate_hp(self):
        return self.base.calculate_hp()

    def calculate_bpm(self):
        return ht_bpm(self.base.calculate_bpm())

    def calculate_length(self):
        return ht_length(self.base.calculate_length())


def mod_calculator_factory(ar, od, cs, hp, bpm, length, mod_val):
    calc = NoMod(ar, od, cs, hp, bpm, length)
    # Apply in correct order: EZ -> HR -> DT/HT
    if mod_val & 2:  # EZ
        calc = Easy(calc)
    if mod_val & 16:  # HR
        calc = HardRock(calc)
    if mod_val & 64:  # DT
        calc = DoubleTime(calc)
    if mod_val & 256:  # HT
        calc = HalfTime(calc)
    return calc
