import { useState } from 'react';
import Icon from '@/components/ui/icon';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

type Screen = 'home' | 'profile' | 'districts' | 'leaderboard' | 'marketplace' | 'wallet';

const Index = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  
  const steps = 7842;
  const stepsGoal = 10000;
  const stepsProgress = (steps / stepsGoal) * 100;
  const tokensEarned = 7.84;
  const tokenBalance = 142.5;

  return (
    <div className="min-h-screen bg-background pb-20">
      {currentScreen === 'home' && <HomeScreen steps={steps} stepsGoal={stepsGoal} stepsProgress={stepsProgress} tokensEarned={tokensEarned} />}
      {currentScreen === 'wallet' && <WalletScreen balance={tokenBalance} />}
      {currentScreen === 'marketplace' && <MarketplaceScreen />}
      {currentScreen === 'profile' && <ProfileScreen />}
      {currentScreen === 'districts' && <DistrictsScreen />}
      {currentScreen === 'leaderboard' && <LeaderboardScreen />}
      
      <BottomNav currentScreen={currentScreen} onNavigate={setCurrentScreen} />
    </div>
  );
};

function HomeScreen({ steps, stepsGoal, stepsProgress, tokensEarned }: { steps: number; stepsGoal: number; stepsProgress: number; tokensEarned: number }) {
  return (
    <div className="animate-fade-in">
      <div className="bg-gradient-to-br from-primary via-primary/90 to-accent p-6 pb-12 rounded-b-[2rem] shadow-lg">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">SPiTAK</h1>
            <p className="text-white/80 text-sm">Двигайся и зарабатывай</p>
          </div>
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20">
            <Icon name="Bell" size={20} />
          </Button>
        </div>

        <div className="relative w-64 h-64 mx-auto mb-6">
          <svg className="transform -rotate-90 w-64 h-64">
            <circle
              cx="128"
              cy="128"
              r="112"
              stroke="rgba(255,255,255,0.2)"
              strokeWidth="16"
              fill="none"
            />
            <circle
              cx="128"
              cy="128"
              r="112"
              stroke="white"
              strokeWidth="16"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 112}`}
              strokeDashoffset={`${2 * Math.PI * 112 * (1 - stepsProgress / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Icon name="Footprints" size={32} className="text-white mb-2" />
            <div className="text-5xl font-bold text-white">{steps.toLocaleString()}</div>
            <div className="text-white/80 text-sm mt-1">из {stepsGoal.toLocaleString()}</div>
          </div>
        </div>

        <div className="flex items-center justify-center gap-2 bg-white/20 backdrop-blur-sm rounded-2xl px-6 py-3 max-w-fit mx-auto">
          <Icon name="Coins" size={20} className="text-yellow-300" />
          <span className="text-white font-semibold">+{tokensEarned} $SPiTAK сегодня</span>
        </div>
      </div>

      <div className="px-6 py-6 space-y-4">
        <Card className="p-4 border-none shadow-md">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-foreground">Boost активен</h3>
            <Badge className="bg-accent text-white">x2</Badge>
          </div>
          <Progress value={65} className="h-2" />
          <p className="text-xs text-muted-foreground mt-2">Осталось 18 минут</p>
        </Card>

        <div className="grid grid-cols-2 gap-4">
          <Card className="p-4 border-none shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon name="TrendingUp" size={20} className="text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">12</p>
                <p className="text-xs text-muted-foreground">Место в городе</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 border-none shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                <Icon name="Flame" size={20} className="text-accent" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">7</p>
                <p className="text-xs text-muted-foreground">Дней streak</p>
              </div>
            </div>
          </Card>
        </div>

        <Button className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity">
          <Icon name="Zap" size={20} className="mr-2" />
          Активировать Boost
        </Button>
      </div>
    </div>
  );
}

function WalletScreen({ balance }: { balance: number }) {
  const weeklyData = [
    { day: 'Пн', amount: 8.2 },
    { day: 'Вт', amount: 12.5 },
    { day: 'Ср', amount: 9.8 },
    { day: 'Чт', amount: 15.3 },
    { day: 'Пт', amount: 11.2 },
    { day: 'Сб', amount: 18.7 },
    { day: 'Вс', amount: 7.8 },
  ];

  const maxAmount = Math.max(...weeklyData.map(d => d.amount));

  return (
    <div className="animate-fade-in px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">Кошелёк</h1>

      <Card className="p-6 mb-6 bg-gradient-to-br from-primary to-accent border-none shadow-lg">
        <p className="text-white/80 text-sm mb-2">Баланс токенов</p>
        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-5xl font-bold text-white">{balance}</span>
          <span className="text-2xl text-white/80">$SPiTAK</span>
        </div>
        <div className="flex items-center gap-2 text-white/90 text-sm">
          <Icon name="TrendingUp" size={16} />
          <span>≈ {(balance * 180).toLocaleString()} AMD</span>
        </div>
      </Card>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Заработок за неделю</h2>
        <Card className="p-6 border-none shadow-md">
          <div className="flex items-end justify-between h-48 gap-2">
            {weeklyData.map((item, idx) => (
              <div key={idx} className="flex flex-col items-center flex-1 gap-2">
                <div
                  className="w-full bg-gradient-to-t from-primary to-accent rounded-t-lg transition-all hover:opacity-80"
                  style={{ height: `${(item.amount / maxAmount) * 100}%` }}
                />
                <span className="text-xs text-muted-foreground">{item.day}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="space-y-3">
        <Button className="w-full h-14 bg-primary text-white hover:bg-primary/90 font-semibold text-lg">
          <Icon name="CreditCard" size={20} className="mr-2" />
          Вывести на карту
        </Button>
        <Button variant="outline" className="w-full h-14 border-2 font-semibold text-lg">
          <Icon name="Lock" size={20} className="mr-2" />
          Застейкать токены
        </Button>
      </div>
    </div>
  );
}

function MarketplaceScreen() {
  const vouchers = [
    { id: 1, brand: 'Yerevan City', discount: '500 AMD', image: '🏙️', price: 2.5, category: 'Супермаркет' },
    { id: 2, brand: 'SAS', discount: '1000 AMD', image: '🛒', price: 5.0, category: 'Супермаркет' },
    { id: 3, brand: 'Zigzag', discount: '15%', image: '👕', price: 8.0, category: 'Одежда' },
    { id: 4, brand: 'Menu.am', discount: '2000 AMD', image: '🍕', price: 10.0, category: 'Еда' },
  ];

  return (
    <div className="animate-fade-in px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Маркетплейс</h1>
      <p className="text-muted-foreground mb-6">Обменивай токены на купоны</p>

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {['Все', 'Еда', 'Супермаркет', 'Одежда', 'Техника'].map((cat) => (
          <Badge key={cat} variant={cat === 'Все' ? 'default' : 'outline'} className="px-4 py-2 whitespace-nowrap cursor-pointer">
            {cat}
          </Badge>
        ))}
      </div>

      <div className="grid gap-4">
        {vouchers.map((voucher) => (
          <Card key={voucher.id} className="p-4 border-none shadow-md hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center text-3xl">
                {voucher.image}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{voucher.brand}</h3>
                <p className="text-muted-foreground text-sm">{voucher.category}</p>
                <p className="text-primary font-bold mt-1">{voucher.discount}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-accent font-bold">
                  <Icon name="Coins" size={18} />
                  <span>{voucher.price}</span>
                </div>
                <Button size="sm" className="mt-2">Купить</Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ProfileScreen() {
  return (
    <div className="animate-fade-in px-6 py-8">
      <div className="flex flex-col items-center mb-8">
        <Avatar className="w-24 h-24 mb-4">
          <AvatarImage src="" />
          <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white text-2xl font-bold">АГ</AvatarFallback>
        </Avatar>
        <h1 className="text-2xl font-bold">Арам Григорян</h1>
        <p className="text-muted-foreground">@aram_grig</p>
        <Badge className="mt-2">KYC Tier 2 ✓</Badge>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <Card className="p-4 text-center border-none shadow-md">
          <p className="text-3xl font-bold text-primary">142.5</p>
          <p className="text-xs text-muted-foreground mt-1">Токенов</p>
        </Card>
        <Card className="p-4 text-center border-none shadow-md">
          <p className="text-3xl font-bold text-accent">7</p>
          <p className="text-xs text-muted-foreground mt-1">Streak</p>
        </Card>
        <Card className="p-4 text-center border-none shadow-md">
          <p className="text-3xl font-bold text-foreground">12</p>
          <p className="text-xs text-muted-foreground mt-1">Место</p>
        </Card>
      </div>

      <div className="space-y-3">
        {[
          { icon: 'User', label: 'Редактировать профиль' },
          { icon: 'Shield', label: 'Пройти KYC' },
          { icon: 'Link', label: 'Реферальная программа' },
          { icon: 'MessageSquare', label: 'Обратная связь' },
          { icon: 'Settings', label: 'Настройки' },
        ].map((item, idx) => (
          <Card key={idx} className="p-4 flex items-center gap-4 border-none shadow-md hover:shadow-lg transition-shadow cursor-pointer">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Icon name={item.icon as any} size={20} className="text-primary" />
            </div>
            <span className="font-medium flex-1">{item.label}</span>
            <Icon name="ChevronRight" size={20} className="text-muted-foreground" />
          </Card>
        ))}
      </div>
    </div>
  );
}

function DistrictsScreen() {
  const districts = [
    { name: 'Арабкир', steps: 2847563, rank: 1, emoji: '🏆' },
    { name: 'Кентрон', steps: 2654321, rank: 2, emoji: '🥈' },
    { name: 'Ачапняк', steps: 2134567, rank: 3, emoji: '🥉' },
    { name: 'Давташен', steps: 1876543, rank: 4, emoji: '4️⃣' },
  ];

  return (
    <div className="animate-fade-in px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Битва районов</h1>
      <p className="text-muted-foreground mb-6">Соревнуйтесь командой за призы</p>

      <Card className="p-6 mb-6 bg-gradient-to-br from-accent to-primary border-none shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-white/80 text-sm">Ваш район</p>
            <h2 className="text-2xl font-bold text-white">Арабкир</h2>
          </div>
          <div className="text-5xl">🏆</div>
        </div>
        <div className="flex items-center gap-2 text-white">
          <Icon name="Users" size={18} />
          <span className="text-sm">342 активных участника</span>
        </div>
      </Card>

      <h2 className="text-lg font-semibold mb-4">Рейтинг районов</h2>
      <div className="space-y-3">
        {districts.map((district) => (
          <Card key={district.name} className="p-4 border-none shadow-md">
            <div className="flex items-center gap-4">
              <div className="text-3xl">{district.emoji}</div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{district.name}</h3>
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Icon name="Footprints" size={14} />
                  <span>{district.steps.toLocaleString()} шагов</span>
                </div>
              </div>
              <div className="text-right">
                <Badge variant={district.rank === 1 ? 'default' : 'outline'}>#{district.rank}</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function LeaderboardScreen() {
  const leaders = [
    { name: 'Тигран А.', steps: 124567, tokens: 124.5, avatar: 'ТА' },
    { name: 'Анна С.', steps: 118932, tokens: 118.9, avatar: 'АС' },
    { name: 'Давид М.', steps: 112345, tokens: 112.3, avatar: 'ДМ' },
    { name: 'Мария К.', steps: 108765, tokens: 108.7, avatar: 'МК' },
    { name: 'Арам Г.', steps: 98432, tokens: 98.4, avatar: 'АГ', isMe: true },
  ];

  return (
    <div className="animate-fade-in px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Рейтинг</h1>
      <p className="text-muted-foreground mb-6">Топ-пользователи Армении</p>

      <div className="space-y-3">
        {leaders.map((leader, idx) => (
          <Card key={idx} className={`p-4 border-none shadow-md ${leader.isMe ? 'ring-2 ring-primary' : ''}`}>
            <div className="flex items-center gap-4">
              <div className="text-xl font-bold text-muted-foreground w-8">#{idx + 1}</div>
              <Avatar>
                <AvatarFallback className={idx < 3 ? 'bg-gradient-to-br from-primary to-accent text-white font-bold' : ''}>{leader.avatar}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="font-semibold">{leader.name}</h3>
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Icon name="Footprints" size={14} />
                  <span>{leader.steps.toLocaleString()}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-accent font-bold">
                  <Icon name="Coins" size={16} />
                  <span>{leader.tokens}</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function BottomNav({ currentScreen, onNavigate }: { currentScreen: Screen; onNavigate: (screen: Screen) => void }) {
  const navItems: { screen: Screen; icon: string; label: string }[] = [
    { screen: 'home', icon: 'Home', label: 'Главная' },
    { screen: 'districts', icon: 'MapPin', label: 'Районы' },
    { screen: 'marketplace', icon: 'ShoppingBag', label: 'Купоны' },
    { screen: 'leaderboard', icon: 'Trophy', label: 'Рейтинг' },
    { screen: 'wallet', icon: 'Wallet', label: 'Кошелёк' },
    { screen: 'profile', icon: 'User', label: 'Профиль' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-border shadow-lg">
      <div className="grid grid-cols-6 gap-1 px-2 py-2">
        {navItems.map((item) => (
          <button
            key={item.screen}
            onClick={() => onNavigate(item.screen)}
            className={`flex flex-col items-center justify-center py-2 px-1 rounded-lg transition-colors ${
              currentScreen === item.screen
                ? 'text-primary bg-primary/10'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Icon name={item.icon as any} size={20} />
            <span className="text-[10px] mt-1 font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default Index;